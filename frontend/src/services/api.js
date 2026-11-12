import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export const getRecommendations = async (userId, topN = 10) => {
  const response = await apiClient.get(`/recommend/${userId}`, {
    params: { top_n: topN }
  })
  return response.data
}

export const postExperiment = async (payload) => {
  const response = await apiClient.post('/experiment', payload)
  return response.data
}

export default apiClient