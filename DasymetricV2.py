#PyQGIS script for SDG15_1_2 Indicator
import os
from qgis.core import *
import processing
from qgis.analysis import *
from processing.core.Processing import Processing
from qgis.PyQt.QtCore import QVariant,QSettings, QTranslator, qVersion, QCoreApplication

## Prepare the environment #ATTENZIONE: DECOMMENTARE LINEE 8-14 PER PIATTAFORMA ESTERNA (VLAB)
qgs = QgsApplication([], False)
qgs.setPrefixPath("/usr", True)
##
## Inizialization
qgs.initQgis()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
#
## Processing init
#input_output
outputs = {}
results = {}
z = QgsVectorLayer("POPBari_2020.zip","POP","ogr")
if not z.isValid():
  print ("Vector layer (population census data) failed to load!")

z1 = QgsVectorLayer("UrbanAtlas.zip","UrbanAtlas","ogr" )
if not z1.isValid():
    print ("Vector layer (Urban Atlas) failed to load!")

zr= QgsRasterLayer("Buildings.zip", "Built-up")
if not zr.isValid():
    print ("Raster layer failed to load!")
    
zr1= QgsRasterLayer("LIDAR_heights.zip", "Building_heights") #questo input dovrebbe essere opzionale
if not zr1.isValid():
    print ("Raster layer failed to load!")

# Riproietta layer
alg_params = {
    'INPUT': z,
    'OPERATION': '',
    'TARGET_CRS': z1,
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['RiproiettaLayer'] = processing.run('native:reprojectlayer', alg_params)

# Calcolatore di campi_censusID
alg_params = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'CENSUS_ID',
    'FIELD_PRECISION': 0,
    'FIELD_TYPE': 1,
    'FORMULA': ' $id ',
    'INPUT': outputs['RiproiettaLayer']['OUTPUT'],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CalcolatoreDiCampi_censusid'] = processing.run('qgis:fieldcalculator', alg_params)

# Estrai/ritaglia da estensione
alg_params = {
    'CLIP': z,
    'EXTENT': z,
    'INPUT': z1,
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['EstrairitagliaDaEstensione'] = processing.run('native:extractbyextent', alg_params)

# Calcolatore campi_class
alg_params = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'BUclass',
    'FIELD_PRECISION': 2,
    'FIELD_TYPE': 2,
    'FORMULA': 'CASE \r\nWHEN \"code_2018\"=\'11100\' THEN \'Res\' \r\nWHEN \"code_2018\"=\'11210\' THEN \'Res\' \r\nWHEN \"code_2018\"=\'11220\' THEN \'Res\'    \r\nWHEN \"code_2018\"=\'11230\' THEN \'Res\' \r\nWHEN \"code_2018\"=\'11240\' THEN \'Res\'\r\nWHEN \"code_2018\"=\'13400\' THEN \'Res\'   \r\nWHEN \"code_2018\"=\'12100\' THEN \'IndCommLei\'\r\nWHEN \"code_2018\"=\'14100\' THEN \'IndCommLei\' \r\nWHEN \"code_2018\"=\'14200\' THEN \'IndCommLei\' \r\nWHEN \"code_2018\"=\'21000\' THEN \'Rural\' \r\nWHEN \"code_2018\"=\'22000\' THEN \'Rural\' \r\nWHEN \"code_2018\"=\'23000\' THEN \'Rural\' \r\nWHEN \"code_2018\"=\'24000\' THEN \'Rural\' \r\nWHEN \"code_2018\"=\'32000\' THEN \'Rural\' \r\nWHEN \"code_2018\"=\'33000\' THEN \'Rural\'\r\nWHEN \"code_2018\"=\'12210\' THEN \'RoadsEt\'\r\nWHEN \"code_2018\"=\'12220\' THEN \'RoadsEt\'\r\nWHEN \"code_2018\"=\'12230\' THEN \'RoadsEt\'\r\nWHEN \"code_2018\"=\'12300\' THEN \'RoadsEt\'\r\nWHEN \"code_2018\"=\'12400\' THEN \'RoadsEt\'     \r\nELSE \'Other\'\r\nEND',
    'INPUT': outputs['EstrairitagliaDaEstensione']['OUTPUT'],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CalcolatoreCampi_class'] = processing.run('qgis:fieldcalculator', alg_params)

# Calcolatore di campi_Factor #ATTENZIONE:per questa parte mi piacerebbe inserire una personalizzazione dei parametri da parte dell'utente(vedi allegato)
alg_params = {
    'FIELD_LENGTH': 2,
    'FIELD_NAME': 'Factor',
    'FIELD_PRECISION': 2,
    'FIELD_TYPE': 0,
    'FORMULA': 'CASE \r\nWHEN \"BUclass\"=\'Res\' THEN 1 \r\nWHEN \"BUclass\"=\'IndCommLei\' THEN 0.1 \r\nWHEN \"BUclass\"=\'Rural\' THEN 0.7    \r\nWHEN \"BUclass\"=\'RoadsEt\' THEN 0.0   \r\nELSE 0.01\r\nEND',
    'INPUT': outputs['CalcolatoreCampi_class']['OUTPUT'],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CalcolatoreDiCampi_factor'] = processing.run('qgis:fieldcalculator', alg_params)

# Crea indice spaziale_census
alg_params = {
    'INPUT': outputs['CalcolatoreDiCampi_censusid']['OUTPUT']
}
outputs['CreaIndiceSpaziale_census'] = processing.run('native:createspatialindex', alg_params)

# Intersezione1
alg_params = {
    'INPUT': outputs['CalcolatoreDiCampi_censusid']['OUTPUT'],
    'INPUT_FIELDS': [''],
    'OVERLAY': outputs['CalcolatoreDiCampi_factor']['OUTPUT'],
    'OVERLAY_FIELDS': [''],
    'OVERLAY_FIELDS_PREFIX': '',
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['Int1'] = processing.run('native:intersection', alg_params)

# Crea reticolo
alg_params = {
    'CRS': z1,
    'EXTENT': z,
    'HOVERLAY': 0,
    'HSPACING': 100,
    'TYPE': 2,
    'VOVERLAY': 0,
    'VSPACING': 100,
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CreaReticolo'] = processing.run('native:creategrid', alg_params)

# Crea indice spaziale_grid
alg_params = {
    'INPUT': outputs['CreaReticolo']['OUTPUT']
}
outputs['CreaIndiceSpaziale_grid'] = processing.run('native:createspatialindex', alg_params)

# Int2
alg_params = {
    'INPUT': outputs['CreaReticolo']['OUTPUT'],
    'INPUT_FIELDS': [''],
    'OVERLAY': outputs['Int1']['OUTPUT'],
    'OVERLAY_FIELDS': [''],
    'OVERLAY_FIELDS_PREFIX': '',
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['Int2'] = processing.run('native:intersection', alg_params)

# Statistiche zonali BUcount
alg_params = {
    'COLUMN_PREFIX': '_',
    'INPUT_RASTER': zr,
    'INPUT_VECTOR': outputs['Int2']['OUTPUT'],
    'RASTER_BAND': 1,
    'STATISTICS': [0]
}
outputs['StatisticheZonaliBucount'] = processing.run('native:zonalstatistics', alg_params)


# Statistiche zonali Hmean ##PASSAGGIO OPZIONALE CHE SI PUò ATTUARE SOLO IN PRESENZA DI DATI SULLE ALTEZZE
alg_params = {
    'COLUMN_PREFIX': 'Hint_',
    'INPUT_RASTER': zr1,
    'INPUT_VECTOR': outputs['Int2']['OUTPUT'],#outputs['StatisticheZonaliBucount']['INPUT_VECTOR'],
    'RASTER_BAND': 1,
    'STATISTICS': [2]
}
outputs['StatisticheZonaliHmean'] = processing.run('native:zonalstatistics', alg_params)

# Calcolatore campo Voladj
alg_params = {
    'FIELD_LENGTH': 10,
    'FIELD_NAME': 'VOL_subel',
    'FIELD_PRECISION': 2,
    'FIELD_TYPE': 0,
    'FORMULA': '\"Factor\"*\"_count\"*100*\"Hint_mean\"',
    'INPUT': outputs['Int2']['OUTPUT'], #outputs['StatisticheZonaliHmean']['INPUT_VECTOR'],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CalcolatoreCampoVoladj'] = processing.run('qgis:fieldcalculator', alg_params)

# Crea indice spaziale_subel
alg_params = {
    'INPUT': outputs['CalcolatoreCampoVoladj']['OUTPUT']
}
outputs['CreaIndiceSpaziale_subel'] = processing.run('native:createspatialindex', alg_params)

# Unisci attributi per posizione (riassunto VOLxCENSUS)
alg_params = {
    'DISCARD_NONMATCHING': False,
    'INPUT': outputs['CalcolatoreDiCampi_censusid']['OUTPUT'],#outputs['CreaIndiceSpaziale_subel']['OUTPUT'],
    'JOIN': outputs['CalcolatoreCampoVoladj']['OUTPUT'],#outputs['CreaIndiceSpaziale_subel']['OUTPUT'],
    'JOIN_FIELDS': ['VOL_subel'],
    'PREDICATE': [0],
    'SUMMARIES': [5],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['UnisciAttributiPerPosizioneRiassuntoVolxcensus'] = processing.run('qgis:joinbylocationsummary', alg_params)

# Unisci attributi secondo il valore del campo
alg_params = {
    'DISCARD_NONMATCHING': False,
    'FIELD': 'CENSUS_ID',
    'FIELDS_TO_COPY': ['VOL_subel_sum'],
    'FIELD_2': 'CENSUS_ID',
    'INPUT': outputs['CalcolatoreCampoVoladj']['OUTPUT'],#outputs['CreaIndiceSpaziale_subel']['OUTPUT'],
    'INPUT_2': outputs['UnisciAttributiPerPosizioneRiassuntoVolxcensus']['OUTPUT'],
    'METHOD': 1,
    'PREFIX': '',
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['UnisciAttributiSecondoIlValoreDelCampo'] = processing.run('native:joinattributestable', alg_params)

# Calcolatore di campi_POPw
alg_params = {
    'FIELD_LENGTH': 7,
    'FIELD_NAME': 'POPw',
    'FIELD_PRECISION': 3,
    'FIELD_TYPE': 0,
    'FORMULA': '(\"POP\" * \"VOL_subel\")/\"VOL_subel_sum\"',
    'INPUT': outputs['UnisciAttributiSecondoIlValoreDelCampo']['OUTPUT'],
    'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
}
outputs['CalcolatoreDiCampi_popw'] = processing.run('qgis:fieldcalculator', alg_params)

# Crea indice spaziale_popw
alg_params = {
    'INPUT': outputs['CalcolatoreDiCampi_popw']['OUTPUT']
}
outputs['CreaIndiceSpaziale_popw'] = processing.run('native:createspatialindex', alg_params)

# Unisci attributi per posizione (riassunto POPxGRID)
alg_params = {
    'DISCARD_NONMATCHING': False,
    'INPUT': outputs['CreaReticolo']['OUTPUT'],
    'JOIN': outputs['CalcolatoreDiCampi_popw']['OUTPUT'],
    'JOIN_FIELDS': ['POPw'],
    'PREDICATE': [0],
    'SUMMARIES': [5],
    'OUTPUT': "POP_GRID.gpkg"
}
outputs['UnisciAttributiPerPosizioneRiassuntoPopxgrid'] = processing.run('qgis:joinbylocationsummary', alg_params)
results['Output'] = outputs['UnisciAttributiPerPosizioneRiassuntoPopxgrid']['OUTPUT'] ### RISULTATO DA SALVARE
##return results
print('All done!')

# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
# print ("success")
qgs.exitQgis()##ATTENZIONE: da decommentare per piattaforma esterna VLAB