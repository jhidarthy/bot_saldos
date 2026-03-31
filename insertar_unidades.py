# insertar_unidades.py

# --- Importaciones de la Base de Datos y Cifrado ---
from database import SessionLocal, UnidadLogin
from utils_cifrado import cifrar_texto
from sqlalchemy.exc import IntegrityError # Para manejar errores de duplicados

# --- LISTA DE UNIDADES A INSERTAR ---
# ❗ ¡Aquí es donde debes poner tus 100 unidades!
# Asegúrate de que cada una tenga un campo "unidad": "numero":y "contrasena".
UNIDADES_A_INSERTAR = [
    {"unidad":"191","numero":"4443926822", "contrasena":"DETFU2020"},
    {"unidad":"205","numero":"4446617624", "contrasena":"DETFU2020"},
    {"unidad":"207","numero":"4446617625", "contrasena":"DETFU2020"},
    {"unidad":"208","numero":"4446619803", "contrasena":"DETFU2020"},
    {"unidad":"209","numero":"4446617620", "contrasena":"DETFU2020"},
    {"unidad":"210","numero":"4443316990", "contrasena":"DETFU2020"},
    {"unidad":"211","numero":"4441778602", "contrasena":"DETFU2020"},
    {"unidad":"9519","numero":"4445727895", "contrasena":"DETFU2020"},
    {"unidad":"11377","numero":"4447037377", "contrasena":"DETFU2020"},
    {"unidad":"12845","numero":"4445099461", "contrasena":"DETFU2020"},
    {"unidad":"15934","numero":"4445100742", "contrasena":"DETFU2020"},
    {"unidad":"17571","numero":"4445125988", "contrasena":"DETFU2020"},
    {"unidad":"17868","numero":"4445083794", "contrasena":"DETFU2020"},
    {"unidad":"17869","numero":"4445085681", "contrasena":"DETFU2020"},
    {"unidad":"17876","numero":"4445863015", "contrasena":"DETFU2020"},
    {"unidad":"18260","numero":"4442347304", "contrasena":"DETFU2020"},
    {"unidad":"18558","numero":"4442133684", "contrasena":"DETFU2020"},
    {"unidad":"18706","numero":"4445863098", "contrasena":"DETFU2020"},
    {"unidad":"18808","numero":"4444468639", "contrasena":"DETFU2020"},
    {"unidad":"21114","numero":"4445122866", "contrasena":"DETFU2020"},
    {"unidad":"21383","numero":"4445127368", "contrasena":"DETFU2020"},
    {"unidad":"21384","numero":"4445127368", "contrasena":"DETFU2020"},
    {"unidad":"21386","numero":"4442361562", "contrasena":"DETFU2020"},
    {"unidad":"21388","numero":"4445118945", "contrasena":"DETFU2020"},
    {"unidad":"21451","numero":"4441948476", "contrasena":"DETFU2020"},
    {"unidad":"21842","numero":"4442202768", "contrasena":"DETFU2020"},
    {"unidad":"22216","numero":"4445862995", "contrasena":"DETFU2020"},
    {"unidad":"22562","numero":"4445097673", "contrasena":"DETFU2020"},
    {"unidad":"22997","numero":"4441761178", "contrasena":"DETFU2020"},
    {"unidad":"23454","numero":"4442923492", "contrasena":"DETFU2020"},
    {"unidad":"23586","numero":"4447057747", "contrasena":"DETFU2020"},
    {"unidad":"25594","numero":"4445411570", "contrasena":"DETFU2020"},
    {"unidad":"25761","numero":"4441913801", "contrasena":"DETFU2020"},
    {"unidad":"26684","numero":"4445080450", "contrasena":"DETFU2020"},
    {"unidad":"27158","numero":"4443158177", "contrasena":"DETFU2020"},
    {"unidad":"27579","numero":"4445374939", "contrasena":"DETFU2020"},
    {"unidad":"27616","numero":"4445863038", "contrasena":"DETFU2020"},
    {"unidad":"27673","numero":"4448598926", "contrasena":"DETFU2020"},
    {"unidad":"29114","numero":"4446616594", "contrasena":"DETFU2020"},
    {"unidad":"29120","numero":"4445413435", "contrasena":"DETFU2020"},
    {"unidad":"29130","numero":"4441948489", "contrasena":"DETFU2020"},
    {"unidad":"29158","numero":"4443178786", "contrasena":"DETFU2020"},
    {"unidad":"30035","numero":"4445027094", "contrasena":"DETFU2020"},
    {"unidad":"30192","numero":"4446616524", "contrasena":"DETFU2020"},
    {"unidad":"30239","numero":"4445862959", "contrasena":"DETFU2020"},
    {"unidad":"30557","numero":"4446616513", "contrasena":"DETFU2020"},
    {"unidad":"30820","numero":"4445443413", "contrasena":"DETFU2020"},
    {"unidad":"30921","numero":"4445413052", "contrasena":"DETFU2020"},
    {"unidad":"30952","numero":"4445073637", "contrasena":"DETFU2020"},
    {"unidad":"31382","numero":"4443188344", "contrasena":"DETFU2020"},
    {"unidad":"31409","numero":"4441784296", "contrasena":"DETFU2020"},
    {"unidad":"31550","numero":"9994396629", "contrasena":"DETFU2020"},
    {"unidad":"31810","numero":"4446616598", "contrasena":"DETFU2020"},
    {"unidad":"31900","numero":"4446631579", "contrasena":"DETFU2020"},
    {"unidad":"32001","numero":"4442342794", "contrasena":"DETFU2020"},
    {"unidad":"32269","numero":"4446616531", "contrasena":"DETFU2020"},
    {"unidad":"32482","numero":"4446616590", "contrasena":"DETFU2020"},
    {"unidad":"32712","numero":"4441893141", "contrasena":"DETFU2020"},
    {"unidad":"33625","numero":"4446616577", "contrasena":"DETFU2020"},
    {"unidad":"33810","numero":"4444269462", "contrasena":"DETFU2020"},
    {"unidad":"35143","numero":"4442146988", "contrasena":"DETFU2020"},
    {"unidad":"35154","numero":"4446500665", "contrasena":"DETFU2020"},
    {"unidad":"35516","numero":"4444362730", "contrasena":"DETFU2020"},
    {"unidad":"35991","numero":"4443928436", "contrasena":"DETFU2020"},
    {"unidad":"36267","numero":"4446616587", "contrasena":"DETFU2020"},
    {"unidad":"37426","numero":"4447060285", "contrasena":"DETFU2020"},
    {"unidad":"37703","numero":"4443416124", "contrasena":"DETFU2020"},
    {"unidad":"38033","numero":"4447060253", "contrasena":"DETFU2020"},
    {"unidad":"38099","numero":"4443176373", "contrasena":"DETFU2020"},
    {"unidad":"38414","numero":"4445863130", "contrasena":"DETFU2020"},
    {"unidad":"38418","numero":"4445063668", "contrasena":"DETFU2020"},
    {"unidad":"38419","numero":"4445737890", "contrasena":"DETFU2020"},
    {"unidad":"38494","numero":"4445075263", "contrasena":"DETFU2020"},
    {"unidad":"38515","numero":"4447063688", "contrasena":"DETFU2020"},
    {"unidad":"38516","numero":"4443177220", "contrasena":"DETFU2020"},
    {"unidad":"38575","numero":"4442410557", "contrasena":"DETFU2020"},
    {"unidad":"39317","numero":"4445393581", "contrasena":"DETFU2020"},
    {"unidad":"39344","numero":"4446616576", "contrasena":"DETFU2020"},
    {"unidad":"39348","numero":"4446616617", "contrasena":"DETFU2020"},
    {"unidad":"39359","numero":"4445411911", "contrasena":"DETFU2020"},
    {"unidad":"39489","numero":"4445738147", "contrasena":"DETFU2020"},
    {"unidad":"39507","numero":"4441958276", "contrasena":"DETFU2020"},
    {"unidad":"39631","numero":"4444287996", "contrasena":"DETFU2020"},
    {"unidad":"39650","numero":"4441894335", "contrasena":"DETFU2020"},
    {"unidad":"39654","numero":"4445449455", "contrasena":"DETFU2020"},
    {"unidad":"39932","numero":"4444363390", "contrasena":"DETFU2020"},
    {"unidad":"39933","numero":"4445442717", "contrasena":"DETFU2020"},
    {"unidad":"39934","numero":"4445439303", "contrasena":"DETFU2020"},
    {"unidad":"40021","numero":"4446616586", "contrasena":"DETFU2020"},
    {"unidad":"40025","numero":"4444533470", "contrasena":"DETFU2020"},
    {"unidad":"40653","numero":"4441924662", "contrasena":"DETFU2020"},
    {"unidad":"40655","numero":"4441358094", "contrasena":"DETFU2020"},
    {"unidad":"40697","numero":"4445844801", "contrasena":"DETFU2020"},
    {"unidad":"41537","numero":"4447060265", "contrasena":"DETFU2020"},
    {"unidad":"41542","numero":"4445436270", "contrasena":"DETFU2020"},
    {"unidad":"41547","numero":"4445862975", "contrasena":"DETFU2020"},
    {"unidad":"41548","numero":"4448564764", "contrasena":"DETFU2020"},
    {"unidad":"41657","numero":"4447060254", "contrasena":"DETFU2020"},
    {"unidad":"41743","numero":"4445861384", "contrasena":"DETFU2020"},
    {"unidad":"41750","numero":"4443182800", "contrasena":"DETFU2020"},
    {"unidad":"41764","numero":"4445844803", "contrasena":"DETFU2020"},
    {"unidad":"41770","numero":"4446616512", "contrasena":"DETFU2020"},
    {"unidad":"41811","numero":"4442004836", "contrasena":"DETFU2020"},
    {"unidad":"41825","numero":"4445861827", "contrasena":"DETFU2020"},
    {"unidad":"41915","numero":"4446616626", "contrasena":"DETFU2020"},
    {"unidad":"41992","numero":"4441882040", "contrasena":"DETFU2020"},
    {"unidad":"41993","numero":"4447083534", "contrasena":"DETFU2020"},
    {"unidad":"42260","numero":"4442923950", "contrasena":"DETFU2020"},
    {"unidad":"42266","numero":"4447090838", "contrasena":"DETFU2020"},
    {"unidad":"42267","numero":"4446616568", "contrasena":"DETFU2020"},
    {"unidad":"42378","numero":"4441832226", "contrasena":"DETFU2020"},
    {"unidad":"42448","numero":"4441761195", "contrasena":"DETFU2020"},
    {"unidad":"42598","numero":"4446607641", "contrasena":"DETFU2020"},
    {"unidad":"42642","numero":"4446631478", "contrasena":"DETFU2020"},
    {"unidad":"43079","numero":"4442994018", "contrasena":"DETFU2020"},
    {"unidad":"43123","numero":"4448564892", "contrasena":"DETFU2020"},
    {"unidad":"43125","numero":"4441778497", "contrasena":"DETFU2020"},
    {"unidad":"43233","numero":"4446631628", "contrasena":"DETFU2020"},
    {"unidad":"43302","numero":"4441948501", "contrasena":"DETFU2020"},
    {"unidad":"43305","numero":"4447068490", "contrasena":"DETFU2020"},
    {"unidad":"43375","numero":"4448561271", "contrasena":"DETFU2020"},
    {"unidad":"43520","numero":"4445862996", "contrasena":"DETFU2020"},
    {"unidad":"43524","numero":"4441948810", "contrasena":"DETFU2020"},
    {"unidad":"43585","numero":"4444472601", "contrasena":"DETFU2020"},
    {"unidad":"43590","numero":"4442228181", "contrasena":"DETFU2020"},
    {"unidad":"43605","numero":"4444287999", "contrasena":"DETFU2020"},
    {"unidad":"43688","numero":"4441949738", "contrasena":"DETFU2020"},
    {"unidad":"43689","numero":"4445738322", "contrasena":"DETFU2020"},
    {"unidad":"43690","numero":"4445862949", "contrasena":"DETFU2020"},
    {"unidad":"44694","numero":"4441731668", "contrasena":"DETFU2020"},
    {"unidad":"44696","numero":"4445765674", "contrasena":"DETFU2020"},
    {"unidad":"44734","numero":"4445443444", "contrasena":"DETFU2020"},
    {"unidad":"44736","numero":"4443159289", "contrasena":"DETFU2020"},
    {"unidad":"44737","numero":"4441763451", "contrasena":"DETFU2020"},
    {"unidad":"44763","numero":"4445450452", "contrasena":"DETFU2020"},
    {"unidad":"44840","numero":"4445393576", "contrasena":"DETFU2020"},
    {"unidad":"45129","numero":"4443342800", "contrasena":"DETFU2020"},
    {"unidad":"45155","numero":"4441948482", "contrasena":"DETFU2020"},
    {"unidad":"45162","numero":"4443178544", "contrasena":"DETFU2020"},
    {"unidad":"45169","numero":"4444361551", "contrasena":"DETFU2020"},
    {"unidad":"45171","numero":"4447060255", "contrasena":"DETFU2020"},
    {"unidad":"45230","numero":"4442351544", "contrasena":"DETFU2020"},
    {"unidad":"45232","numero":"4446616567", "contrasena":"DETFU2020"},
    {"unidad":"45239","numero":"4442892494", "contrasena":"DETFU2020"},
    {"unidad":"45241","numero":"4447032055", "contrasena":"DETFU2020"},
    {"unidad":"45475","numero":"4443897039", "contrasena":"DETFU2020"},
    {"unidad":"45652","numero":"4445063151", "contrasena":"DETFU2020"},
    {"unidad":"45700","numero":"4447066643", "contrasena":"DETFU2020"},
    {"unidad":"47979","numero":"4443188589", "contrasena":"DETFU2020"},
    {"unidad":"48057","numero":"4446500642", "contrasena":"DETFU2020"},
    {"unidad":"48078","numero":"4445765748", "contrasena":"DETFU2020"},
    {"unidad":"48117","numero":"4445393569", "contrasena":"DETFU2020"},
    {"unidad":"48118","numero":"4442393396", "contrasena":"DETFU2020"},
    {"unidad":"48244","numero":"4445863094", "contrasena":"DETFU2020"},
    {"unidad":"48366","numero":"4446616525", "contrasena":"DETFU2020"},
    {"unidad":"48498","numero":"4446500594", "contrasena":"DETFU2020"},
    {"unidad":"49147","numero":"4446631513", "contrasena":"DETFU2020"},
    {"unidad":"49312","numero":"4443101482", "contrasena":"DETFU2020"},
    {"unidad":"49436","numero":"4441841684", "contrasena":"DETFU2020"},
    {"unidad":"49449","numero":"4442085955", "contrasena":"DETFU2020"},
    {"unidad":"49699","numero":"4445442947", "contrasena":"DETFU2020"},
    {"unidad":"50057","numero":"4441948646", "contrasena":"DETFU2020"},
    {"unidad":"50058","numero":"4445097558", "contrasena":"DETFU2020"},
    {"unidad":"50913","numero":"4445098468", "contrasena":"DETFU2020"},
    {"unidad":"51671","numero":"4444538958", "contrasena":"DETFU2020"},
    {"unidad":"53038","numero":"4441948411", "contrasena":"DETFU2020"},
    {"unidad":"56501","numero":"4442923976", "contrasena":"DETFU2020"},
    {"unidad":"56999","numero":"4445844800", "contrasena":"DETFU2020"},
    {"unidad":"57535","numero":"4441948559", "contrasena":"DETFU2020"},
    {"unidad":"57537","numero":"4446517009", "contrasena":"DETFU2020"},
    {"unidad":"57581","numero":"4441846647", "contrasena":"DETFU2020"},
    {"unidad":"57639","numero":"4445863021", "contrasena":"DETFU2020"},
    {"unidad":"57640","numero":"4445863024", "contrasena":"DETFU2020"},
    {"unidad":"57660","numero":"4441913159", "contrasena":"DETFU2020"},
    {"unidad":"57795","numero":"4443928440", "contrasena":"DETFU2020"},
    {"unidad":"57797","numero":"4446631604", "contrasena":"DETFU2020"},
    {"unidad":"57798","numero":"4441700893", "contrasena":"DETFU2020"},
    {"unidad":"57806","numero":"4444276016", "contrasena":"DETFU2020"},
    {"unidad":"57809","numero":"4446612144", "contrasena":"DETFU2020"},
    {"unidad":"57811","numero":"4446614113", "contrasena":"DETFU2020"},
    {"unidad":"57812","numero":"4446614106", "contrasena":"DETFU2020"},
    {"unidad":"57813","numero":"4446617858", "contrasena":"DETFU2020"},
    {"unidad":"57814","numero":"4446617859", "contrasena":"DETFU2020"},
    {"unidad":"57826","numero":"4441338118", "contrasena":"DETFU2020"},
    {"unidad":"57842","numero":"4445847079", "contrasena":"DETFU2020"},
    {"unidad":"57843","numero":"4441344400", "contrasena":"DETFU2020"},
    {"unidad":"57847","numero":"4441345929", "contrasena":"DETFU2020"},
    {"unidad":"57850","numero":"4444363569", "contrasena":"DETFU2020"},
    {"unidad":"57851","numero":"4444526665", "contrasena":"DETFU2020"},
    {"unidad":"57853","numero":"4445414687", "contrasena":"DETFU2020"},
    {"unidad":"57855","numero":"4445072256", "contrasena":"DETFU2020"},
    {"unidad":"57860","numero":"4442207306", "contrasena":"DETFU2020"},
    {"unidad":"57862","numero":"4446631538", "contrasena":"DETFU2020"},
    {"unidad":"57867","numero":"4446631655", "contrasena":"DETFU2020"},
    {"unidad":"57869","numero":"4444278767", "contrasena":"DETFU2020"},
    {"unidad":"57891","numero":"4445441624", "contrasena":"DETFU2020"},
    {"unidad":"57894","numero":"4442191673", "contrasena":"DETFU2020"},
    {"unidad":"57896","numero":"4446631455", "contrasena":"DETFU2020"},
    {"unidad":"57907","numero":"4442191723", "contrasena":"DETFU2020"},
    {"unidad":"57916","numero":"4446500664", "contrasena":"DETFU2020"},
    {"unidad":"57917","numero":"4444269459", "contrasena":"DETFU2020"},
    {"unidad":"58620","numero":"4445400093", "contrasena":"DETFU2020"},
    {"unidad":"58622","numero":"4443489741", "contrasena":"DETFU2020"},
    {"unidad":"58631","numero":"4445118859", "contrasena":"DETFU2020"},
    {"unidad":"58633","numero":"4444279504", "contrasena":"DETFU2020"},
    {"unidad":"58637","numero":"4445115494", "contrasena":"DETFU2020"},
    {"unidad":"58640","numero":"4445103565", "contrasena":"DETFU2020"},
    {"unidad":"58641","numero":"4442091566", "contrasena":"DETFU2020"},
    {"unidad":"58642","numero":"4442191361", "contrasena":"DETFU2020"},
    {"unidad":"58646","numero":"4442227152", "contrasena":"DETFU2020"},
    {"unidad":"58649","numero":"4443176128", "contrasena":"DETFU2020"},
    {"unidad":"58660","numero":"4445863348", "contrasena":"DETFU2020"},
    {"unidad":"58662","numero":"4443158053", "contrasena":"DETFU2020"},
    {"unidad":"58692","numero":"4445738081", "contrasena":"DETFU2020"},
    {"unidad":"58719","numero":"4445765893", "contrasena":"DETFU2020"},
    {"unidad":"58736","numero":"4445436276", "contrasena":"DETFU2020"},
    {"unidad":"59046","numero":"4445443808", "contrasena":"DETFU2020"},
    {"unidad":"59153","numero":"4444288003", "contrasena":"DETFU2020"},
    {"unidad":"59207","numero":"4871127244", "contrasena":"DETFU2020"},
    {"unidad":"59230","numero":"4446698629", "contrasena":"DETFU2020"},
    {"unidad":"59355","numero":"4445438453", "contrasena":"DETFU2020"},
    {"unidad":"59361","numero":"4446631645", "contrasena":"DETFU2020"},
    {"unidad":"59475","numero":"4442194381", "contrasena":"DETFU2020"},
    {"unidad":"59480","numero":"4442993986", "contrasena":"DETFU2020"},
    {"unidad":"59511","numero":"4448299082", "contrasena":"DETFU2020"},
    {"unidad":"59533","numero":"4445103295", "contrasena":"DETFU2020"},
    {"unidad":"59547","numero":"4448607191", "contrasena":"DETFU2020"},
    {"unidad":"59637","numero":"4447084044", "contrasena":"DETFU2020"},
    {"unidad":"59663","numero":"4443085239", "contrasena":"DETFU2020"},
    {"unidad":"59850","numero":"4443336369", "contrasena":"DETFU2020"},
    {"unidad":"59852","numero":"4443387952", "contrasena":"DETFU2020"},
]
# ----------------------------------------

def poblar_base_de_datos():
    """
    Lee la lista de unidades, cifra sus contraseñas y las inserta en la
    tabla 'unidades_login'. Evita insertar registros duplicados.
    """
    print("Iniciando script para poblar la base de datos de credenciales.")
    db = SessionLocal() # Abre la conexión
    
    unidades_insertadas = 0
    unidades_omitidas = 0
    
    try:
        total = len(UNIDADES_A_INSERTAR)
        print(f"Se intentarán procesar {total} unidades.")
        
        for i, datos_unidad in enumerate(UNIDADES_A_INSERTAR):
            unidad_nombre = datos_unidad["unidad"]
            numero_cel = datos_unidad["numero"]
            contrasena_plana = datos_unidad["contrasena"]
            
            print(f"\nProcesando {i+1}/{total}: Unidad '{unidad_nombre}'...")

            # 1. Cifrar la contraseña usando la función de utils_cifrado.py
            contrasena_cifrada = cifrar_texto(contrasena_plana)

            # 2. Crear el objeto que se insertará en la BD
            nueva_unidad = UnidadLogin(
                unidad=unidad_nombre,
                numero_celular=numero_cel,
                contrasena=contrasena_cifrada
            )
            
            # 3. Añadir el nuevo objeto a la "sala de espera" de la BD
            db.add(nueva_unidad)
            
            try:
                # 4. Intentar guardar (commit) el registro en la base de datos
                db.commit()
                print(f"  ✅ ¡Éxito! Unidad '{unidad_nombre}' insertada.")
                unidades_insertadas += 1
            except IntegrityError:
                # Esto ocurre si la 'unidad' o el 'numero_celular' ya existen.
                db.rollback() # Revierte el intento de inserción fallido
                print(f"  ⚠️  OMITIDO: La unidad o el número ya existen en la BD.")
                unidades_omitidas += 1

    except Exception as e:
        print(f"❌ Ocurrió un error crítico: {e}")
        db.rollback() # Revierte todos los cambios si algo grave falla
    finally:
        db.close() # Asegura que la conexión siempre se cierre
        print("\n" + "="*50)
        print("✅ PROCESO DE INSERCIÓN COMPLETADO.")
        print(f"   - Unidades nuevas insertadas: {unidades_insertadas}")
        print(f"   - Unidades omitidas (duplicadas): {unidades_omitidas}")
        print("="*50)

# --- EJECUCIÓN DEL SCRIPT ---
if __name__ == "__main__":
    poblar_base_de_datos()