import streamlit as st
import requests

# Configuración de la API
API_URL = "https://cx6uoml6xa.execute-api.us-east-1.amazonaws.com/default/lbreconocimiento"

st.set_page_config(layout="wide", page_title="Detector de Placas")

# Títulos
st.markdown("<h1 style='text-align: center;'>🚗 Detector de Placas de Auto</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Sube la foto de un vehículo para identificar su matrícula</h2>", unsafe_allow_html=True)

# Inicializar historial en la sesión
if "historial_placas" not in st.session_state:
    st.session_state.historial_placas = []

# Diseño de columnas
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📤 Panel de Carga")
    uploaded_file = st.file_uploader("Sube una imagen (JPG, JPEG, PNG)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Mostrar vista previa de la imagen cargada
        st.image(uploaded_file, caption="Imagen seleccionada", use_container_width=True)
        
        # Botón para procesar (opcional, pero ayuda a evitar llamadas accidentales)
        if st.button("🔍 Detectar Placa"):
            image_bytes = uploaded_file.read()
            
            try:
                with st.spinner("🔄 Analizando imagen con AWS Rekognition..."):
                    # Enviar imagen a la API Lambda
                    response = requests.post(
                        API_URL, 
                        data=image_bytes, 
                        headers={"Content-Type": "application/octet-stream"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Guardar en el historial
                        resultado = {
                            "url": data.get("image_url"),
                            "placa": data.get("placa", "No detectada")
                        }
                        st.session_state.historial_placas.append(resultado)
                        
                        # Mostrar resultado inmediato
                        if resultado["placa"] != "No se detectó placa":
                            st.success(f"✅ ¡Placa detectada!: **{resultado['placa']}**")
                        else:
                            st.warning("⚠️ No se encontró ninguna placa con formato ABC-123.")
                    else:
                        st.error(f"❌ Error en la API: {response.status_code}")
                        
            except Exception as e:
                st.error(f"❌ Error de conexión: {str(e)}")

with col2:
    st.subheader("🕒 Historial de Consultas")
    
    if st.session_state.historial_placas:
        # Mostrar el historial del más reciente al más antiguo
        for i, item in enumerate(reversed(st.session_state.historial_placas)):
            with st.expander(f"Resultado #{len(st.session_state.historial_placas) - i}: {item['placa']}", expanded=True):
                st.image(item["url"], use_container_width=True)
                st.write(f"**Matrícula:** `{item['placa']}`")
                st.markdown(f"[🔗 Abrir imagen original]({item['url']})")
                st.divider()
    else:
        st.info("Aún no hay detecciones en esta sesión.")