# [?] Fix select GPU index other than 0 software crash problem

## Summary
Severity: Unknown
Chain: Zilliqa
Component: Zilliqa/zq1
Published: 2018-12-08
Source: https://github.com/Zilliqa/zq1/commit/89d373966ce0236b22a8b4bc4acc6bca388363ae
Type: security-commit

## Details
Fix select GPU index other than 0 software crash problem

## Patch
### src/depends/libethash-cuda/CUDAMiner.cpp
```diff
@@ -441,6 +441,11 @@ bool CUDAMiner::mine(const WorkPackage &w, Solution &solution)
         }
     }
 
+    // Zilliqa mining is create mining thread every time need to do POW.
+    // So need to set the device to use every time.
+    unsigned device = s_devices[m_index] > -1 ? s_devices[m_index] : m_index;
+    CUDA_SAFE_CALL(cudaSetDevice(device));
+
     // Persist most recent job anyway. No need to do another
     // conditional check if they're different
     m_currentWP = w;
```

### src/libPOW/pow.cpp
```diff
@@ -406,9 +406,11 @@ void POW::InitOpenCL() {
     LOG_GENERAL(FATAL, "Failed to configure OpenCL GPU, please check hardware");
   }
 
-  CLMiner::setNumInstances(UINT_MAX);
   auto gpuToUse = GetGpuToUse();
   auto totalGpuDevice = CLMiner::getNumDevices();
+
+  CLMiner::setNumInstances(gpuToUse.size());
+
   for (const auto gpuIndex : gpuToUse) {
     if (gpuIndex >= totalGpuDevice) {
       LOG_GENERAL(FATAL, "Selected GPU "
@@ -433,19 +435,24 @@ void POW::InitCUDA() {
 #ifdef CUDA_MINE
   using namespace dev::eth;
 
+  auto gpuToUse = GetGpuToUse();
+  auto deviceGenerateDag = *gpuToUse.begin();
+  LOG_GENERAL(INFO, "Generate dag Nvidia GPU #" << deviceGenerateDag);
+
   if (!CUDAMiner::configureGPU(CUDA_BLOCK_SIZE, CUDA_GRID_SIZE, CUDA_STREAM_NUM,
-                               CUDA_SCHEDULE_FLAG, 0, 0, false, false)) {
+                               CUDA_SCHEDULE_FLAG, 0, deviceGenerateDag, false,
+                               false)) {
     LOG_GENERAL(FATAL, "Failed to configure CUDA GPU, please check hardware");
   }
 
-  CUDAMiner::setNumInstances(UINT_MAX);
-  auto gpuToUse = GetGpuToUse();
+  CUDAMiner::setNumInstances(gpuToUse.size());
+
   auto totalGpuDevice = CUDAMiner::getNumDevices();
   for (const auto gpuIndex : gpuToUse) {
     if (gpuIndex >= totalGpuDevice) {
       LOG_GENERAL(FATAL, "Selected GPU "
                              << gpuIndex
-                             << " exceed the physical OpenCL GPU number "
+                             << " exceed the physical Nvidia GPU number "
                              << totalGpuDevice);
     }
 
@@ -469,5 +476,10 @@ std::set<unsigned int> POW::GetGpuToUse() {
     unsigned int index = strtol(item.c_str(), NULL, 10);
     gpuToUse.insert(index);
   }
+
+  if (gpuToUse.empty()) {
+    LOG_GENERAL(FATAL, "Please select at least one GPU to use.");
+  }
+
   return gpuToUse;
 }
\ No newline at end of file
```
