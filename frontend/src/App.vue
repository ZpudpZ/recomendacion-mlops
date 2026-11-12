<!-- Ubicación: frontend/src/App.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { getRecommendations, postExperiment } from './services/api'
import ExperimentControl from './components/ExperimentControl.vue'
import KpiDashboard from './components/KpiDashboard.vue'
import RecommendationGrid from './components/RecommendationGrid.vue'

const kpis = ref({
  rmse: 0.9352,
  mae: 0.7378,
  sparsity_pct: 93.7,
  compute_time_ms: 0.0,
  train_samples: 80000,
  test_samples: 20000,
  n_users: 943,
  n_items: 1682
})

const recommendations = ref([])
const isColdStart = ref(false)
const queriedUser = ref(196)
const topN = ref(10)
const userInteractionsCount = ref(0)

const expLoading = ref(false)
const recLoading = ref(false)
const errorMessage = ref('')
const systemStatus = ref('SISTEMA EN LÍNEA | MOTOR SVD OPERATIVO')

const handleExperiment = async (hyperparams) => {
  expLoading.value = true
  errorMessage.value = ''
  systemStatus.value = 'EJECUTANDO VALIDACIÓN EXPERIMENTAL SVD...'

  try {
    const data = await postExperiment(hyperparams)
    kpis.value = data
    systemStatus.value = `VALIDACIÓN COMPLETADA EN ${data.compute_time_ms} MS`
    if (hyperparams.update_active_model) {
      await handleRecommendations({ userId: queriedUser.value, topN: topN.value })
    }
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      'Error al ejecutar el experimento en el servidor de inferencia.'
    systemStatus.value = 'ERROR EN PIPELINE DE EXPERIMENTACIÓN'
  } finally {
    expLoading.value = false
  }
}

const handleRecommendations = async ({ userId, topN: requestedTopN }) => {
  recLoading.value = true
  errorMessage.value = ''
  queriedUser.value = userId
  topN.value = requestedTopN

  try {
    const data = await getRecommendations(userId, requestedTopN)
    recommendations.value = data.recommendations
    isColdStart.value = data.is_cold_start
    userInteractionsCount.value = data.user_interactions_count || 0
  } catch (err) {
    errorMessage.value =
      err.response?.data?.detail ||
      'Error al consultar recomendaciones en el servidor.'
    recommendations.value = []
  } finally {
    recLoading.value = false
  }
}

onMounted(async () => {
  await handleRecommendations({ userId: queriedUser.value, topN: topN.value })
  await handleExperiment({
    n_factors: 100,
    n_epochs: 20,
    lr_all: 0.005,
    reg_all: 0.02,
    test_split: 0.2,
    sample_fraction: 0.6,
    update_active_model: true
  })
})
</script>

<template>
  <div class="enterprise-shell">
    <header class="navbar">
      <div class="brand-group">
        <span class="status-indicator"></span>
        <div>
          <h1>ENTERPRISE MLOPS // COLLABORATIVE FILTERING ENGINE</h1>
          <p>Arquitectura Modular SVD · FastAPI Backend · Vue 3 Composition API</p>
        </div>
      </div>
      <div class="status-box">
        <span>{{ systemStatus }}</span>
      </div>
    </header>

    <div v-if="errorMessage" class="error-banner">
      {{ errorMessage }}
    </div>

    <main class="layout-grid">
      <ExperimentControl
        :loading="expLoading"
        @run-experiment="handleExperiment"
      />

      <div class="workspace-column">
        <KpiDashboard :kpis="kpis" />

        <RecommendationGrid
          :recommendations="recommendations"
          :is-cold-start="isColdStart"
          :queried-user="queriedUser"
          :user-interactions-count="userInteractionsCount"
          :loading="recLoading"
          @fetch-recommendations="handleRecommendations"
        />
      </div>
    </main>
  </div>
</template>

<style scoped>
:global(*) {
  box-sizing: border-box;
}

:global(body) {
  margin: 0;
  background-color: #0f172a;
  color: #f8fafc;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.enterprise-shell {
  min-height: 100vh;
  max-width: 1600px;
  margin: 0 auto;
  padding: 1.25rem 1.5rem 2rem;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.9rem 1.25rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.brand-group {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.status-indicator {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: #10b981;
}

.brand-group h1 {
  margin: 0;
  font-size: 1rem;
  letter-spacing: 0.06em;
  color: #f8fafc;
}

.brand-group p {
  margin: 0.15rem 0 0;
  font-size: 0.76rem;
  color: #94a3b8;
}

.status-box {
  font-family: monospace;
  font-size: 0.75rem;
  background-color: #0f172a;
  color: #10b981;
  border: 1px solid #334155;
  padding: 0.4rem 0.75rem;
  border-radius: 0.375rem;
}

.error-banner {
  background-color: rgba(239, 68, 68, 0.12);
  border: 1px solid #ef4444;
  color: #fca5a5;
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.25rem;
  font-size: 0.85rem;
}

.layout-grid {
  display: grid;
  grid-template-columns: 340px 1fr;
  gap: 1.25rem;
  align-items: start;
}

.workspace-column {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

@media (max-width: 1150px) {
  .layout-grid {
    grid-template-columns: 1fr;
  }
}
</style>