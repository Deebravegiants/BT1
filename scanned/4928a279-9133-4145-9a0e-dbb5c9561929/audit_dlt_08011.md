# [?] fix: 25204 Fix race condition in file assignment and reduce consolidation aggressiveness (#25216)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2026-05-04
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/91d90deb6cfb3a82c7f6ac66148038fdf0c49ead
Type: security-commit

## Details
fix: 25204 Fix race condition in file assignment and reduce consolidation aggressiveness (#25216)

Signed-off-by: Ivan Malygin <ivan@swirldslabs.com>

## Patch
### platform-sdk/swirlds-merkledb/src/main/java/com/swirlds/merkledb/MerkleDbCompactionCoordinator.java
```diff
@@ -347,14 +347,25 @@ synchronized void submitCompactionTasks(
                 executor.submit(new CompactionTask(taskKey, levelKey, level, groups.get(i), compactorFactory, config));
             }
 
+            final List<Integer> fileIndices =
+                    eligible.stream().map(DataFileReader::getIndex).toList();
             if (groups.size() > 1) {
                 logger.info(
                         MERKLE_DB.getMarker(),
-                        "[{}] Submitted {} compaction tasks for level {} ({} eligible files)",
+                        "[{}] Submitted {} compaction tasks for level {} ({} eligible files - {})",
                         storeName,
                         groups.size(),
                         level,
-                        eligible.size());
+                        eligible.size(),
+                        fileIndices);
+            } else {
+                logger.info(
+                        MERKLE_DB.getMarker(),
+                        "[{}] Submitted a compaction tasks for level {} ({} eligible files - {})",
+                        storeName,
+                        level,
+                        eligible.size(),
+                        fileIndices);
             }
         }
         // Second pass: consolidation of small files regardless of garbage ratio
@@ -580,6 +591,16 @@ private void submitConsolidationTasks(
             if (alreadyAssigned.contains(reader)) {
                 continue;
             }
+            // If we include files at level 0, the consolidation gets too aggressive and does a lot of unnecessary work
+            // -
+            // level 0 files are naturally smaller, most likely will get stale soon and should be handled by either
+            // compaction or be absorbed.
+            // Without this limitation, consolidation would take care of these files as soon as the counter reaches
+            // minFileCount which
+            // oftentimes is unnecessary.
+            if (fs.compactionLevel() == 0) {
+                continue;
+            }
             if (reader.getSize() < consolidationMaxInputSizeBytes) {
                 smallFilesByLevel
                         .computeIfAbsent(fs.compactionLevel(), _ -> new ArrayList<>())
@@ -704,6 +725,7 @@ private class CompactionTask implements Callable<Boolean> {
 
         @Override
         public Boolean call() {
+            boolean success = false;
             try {
                 // Create a compactor and register it for pause/resume/interrupt
                 final DataFileCompactor compactor = compactorFactory.get();
@@ -717,24 +739,29 @@ public Boolean call() {
                 // Filter out files that were already compacted and deleted since the scan
                 final Set<DataFileReader> currentFiles =
                         new HashSet<>(compactor.getDataFileCollection().getAllCompletedFiles());
-                final List<DataFileReader> validFiles =
-                        assignedFiles.stream().filter(currentFiles::contains).toList();
+                final List<DataFileReader> validFiles = assignedFiles.stream()
+                        .filter(currentFiles::contains)
+                        // Mark files as being compacted — scanner will skip them
+                        // If the file is already being compacted, skip it
+                        .filter(DataFileReader::setCompactionInProgress)
+                        .toList();
                 if (validFiles.isEmpty()) {
                     return false;
                 }
 
-                // Mark files as being compacted — scanner will skip them
-                validFiles.forEach(DataFileReader::setCompactionInProgress);
                 final int targetLevel = Math.min(sourceLevel + 1, config.maxCompactionLevel());
-                return compactor.compactSingleLevel(validFiles, targetLevel);
+                success = compactor.compactSingleLevel(validFiles, targetLevel);
+                return success;
 
             } catch (final InterruptedException | ClosedByInterruptException e) {
                 logger.info(MERKLE_DB.getMarker(), "Interrupted while compacting [{}], this is allowed", taskKey);
             } catch (Exception e) {
                 logger.error(EXCEPTION.getMarker(), "[{}] Compaction failed", taskKey, e);
             } finally {
-                // Reset flag so files become visible to scanner again if compaction failed
-                assignedFiles.forEach(DataFileReader::resetCompactionInProgress);
+                if (!success) {
+                    // Reset flag so files become visible to scanner again if compaction failed
+                    assignedFiles.forEach(DataFileReader::resetCompactionInProgress);
+                }
                 synchronized (MerkleDbCompactionCoordinator.this) {
                     compactorsByName.remove(taskKey);
                     taskKeys.remove(taskKey);
```

### platform-sdk/swirlds-merkledb/src/main/java/com/swirlds/merkledb/files/DataFileReader.java
```diff
@@ -179,9 +179,10 @@ void setFileCompleted() {
 
     /**
      * Marks this file as being actively compacted.
+     * @return {@code true} if the compaction flag successfully updated from {@code false} to {@code true}
      */
-    public void setCompactionInProgress() {
-        compactionInProgress.set(true);
+    public boolean setCompactionInProgress() {
+        return compactionInProgress.compareAndSet(false, true);
     }
 
     /**
```

### platform-sdk/swirlds-merkledb/src/test/java/com/swirlds/merkledb/MerkleDbCompactionCoordinatorTest.java
```diff
@@ -35,6 +35,7 @@
 import java.util.concurrent.CountDownLatch;
 import java.util.concurrent.ThreadPoolExecutor;
 import java.util.concurrent.TimeUnit;
+import java.util.concurrent.atomic.AtomicBoolean;
 import java.util.concurrent.atomic.AtomicInteger;
 import java.util.function.Supplier;
 import org.junit.jupiter.api.AfterEach;
@@ -327,7 +328,7 @@ void testConsolidationSubmitsTaskForSmallFiles() throws InterruptedException, IO
         final List<DataFileReader> smallFiles = new ArrayList<>();
         final List<StatsEntry> statsEntries = new ArrayList<>();
         for (int i = 1; i <= 12; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024); // 5 MB
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024); // 5 MB
             smallFiles.add(f);
             statsEntries.add(new StatsEntry(f, 100)); // all alive → d/a = 0.0
         }
@@ -359,11 +360,9 @@ void testConsolidationSubmitsTaskForSmallFiles() throws InterruptedException, IO
     void testConsolidationSkipsWhenBelowMinFileCount() throws InterruptedException, IOException {
         // 5 small files, but minFileCount = 10 → no consolidation
         final MerkleDbConfig consolidationConfig = configWithConsolidation(50, 10);
-        final List<DataFileReader> smallFiles = new ArrayList<>();
         final List<StatsEntry> statsEntries = new ArrayList<>();
         for (int i = 1; i <= 5; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024);
-            smallFiles.add(f);
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024);
             statsEntries.add(new StatsEntry(f, 100));
         }
 
@@ -385,12 +384,12 @@ void testConsolidationSkipsFilesAboveSizeThreshold() throws InterruptedException
         final List<DataFileReader> files = new ArrayList<>();
         final List<StatsEntry> statsEntries = new ArrayList<>();
         for (int i = 1; i <= 10; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024); // 5 MB
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024); // 5 MB
             files.add(f);
             statsEntries.add(new StatsEntry(f, 100));
         }
-        final DataFileReader large1 = mockFileReader(11, 0, 100, 100 * 1024 * 1024); // 100 MB
-        final DataFileReader large2 = mockFileReader(12, 0, 100, 100 * 1024 * 1024); // 100 MB
+        final DataFileReader large1 = mockFileReader(11, 1, 100, 100 * 1024 * 1024); // 100 MB
+        final DataFileReader large2 = mockFileReader(12, 1, 100, 100 * 1024 * 1024); // 100 MB
         files.add(large1);
         files.add(large2);
         statsEntries.add(new StatsEntry(large1, 100));
@@ -431,16 +430,16 @@ void testConsolidationSkipsFilesAlreadyAssignedToGarbageTasks() throws Interrupt
         final List<StatsEntry> statsEntries = new ArrayList<>();
 
         // 2 dirty files at level 1 (d/a > 0.5)
-        final DataFileReader dirty1 = mockFileReader(1, 1, 100, 5 * 1024 * 1024);
-        final DataFileReader dirty2 = mockFileReader(2, 1, 100, 5 * 1024 * 1024);
+        final DataFileReader dirty1 = mockFileReader(1, 2, 100, 5 * 1024 * 1024);
+        final DataFileReader dirty2 = mockFileReader(2, 3, 100, 5 * 1024 * 1024);
         files.add(dirty1);
         files.add(dirty2);
         statsEntries.add(new StatsEntry(dirty1, 20)); // d/a = 4.0
         statsEntries.add(new StatsEntry(dirty2, 20)); // d/a = 4.0
 
         // 10 clean files (d/a = 0.0)
         for (int i = 3; i <= 12; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024);
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024);
             files.add(f);
             statsEntries.add(new StatsEntry(f, 100));
         }
@@ -485,7 +484,7 @@ void testConsolidationDisabledWhenMaxInputSizeIsZero() throws InterruptedExcepti
         final List<DataFileReader> files = new ArrayList<>();
         final List<StatsEntry> statsEntries = new ArrayList<>();
         for (int i = 1; i <= 20; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 1024); // 1 KB — tiny
+            final DataFileReader f = mockFileReader(i, 1, 100, 1024); // 1 KB — tiny
             files.add(f);
             statsEntries.add(new StatsEntry(f, 100)); // all alive
         }
@@ -500,6 +499,75 @@ void testConsolidationDisabledWhenMaxInputSizeIsZero() throws InterruptedExcepti
         verify(compactor, never()).compactSingleLevel(anyList(), anyInt());
     }
 
+    @Test
+    void testConsolidationSkipsLevelZeroFiles() throws InterruptedException, IOException {
+        // 15 small clean files at level 0 — enough to trigger consolidation by count,
+        // but level 0 should be excluded from consolidation entirely
+        final MerkleDbConfig consolidationConfig = configWithConsolidation(50, 10);
+        final List<StatsEntry> statsEntries = new ArrayList<>();
+        for (int i = 1; i <= 15; i++) {
+            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024); // 5 MB, level 0
+            statsEntries.add(new StatsEntry(f, 100)); // all alive → d/a = 0.0
+        }
+
+        publishScanStats(ID_TO_HASH_CHUNK, buildStats(statsEntries.toArray(StatsEntry[]::new)));
+
+        final DataFileCompactor compactor = mock(DataFileCompactor.class);
+        coordinator.submitCompactionTasks(ID_TO_HASH_CHUNK, () -> compactor, consolidationConfig);
+
+        coordinator.awaitForCurrentCompactionsToComplete(2000);
+
+        // No tasks should be submitted — all files are level 0
+        verify(compactor, never()).compactSingleLevel(anyList(), anyInt());
+    }
+
+    @Test
+    void testConsolidationSkipsLevelZeroButProcessesHigherLevels() throws InterruptedException, IOException {
+        // Mix of level 0 and level 1 small files — only level 1 should be consolidated
+        final MerkleDbConfig consolidationConfig = configWithConsolidation(50, 10);
+        final List<DataFileReader> files = new ArrayList<>();
+        final List<StatsEntry> statsEntries = new ArrayList<>();
+
+        // 15 files at level 0 (should be skipped)
+        for (int i = 1; i <= 15; i++) {
+            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024);
+            files.add(f);
+            statsEntries.add(new StatsEntry(f, 100));
+        }
+
+        // 12 files at level 1 (should be consolidated)
+        for (int i = 16; i <= 27; i++) {
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024);
+            files.add(f);
+            statsEntries.add(new StatsEntry(f, 100));
+        }
+
+        final DataFileCollection fileCollection = mock(DataFileCollection.class);
+        when(fileCollection.getAllCompletedFiles()).thenReturn(files);
+
+        publishScanStats(ID_TO_HASH_CHUNK, buildStats(statsEntries.toArray(StatsEntry[]::new)));
+
+        final CountDownLatch taskDone = new CountDownLatch(1);
+        final List<DataFileReader> compactedFiles = new ArrayList<>();
+        final DataFileCompactor compactor = mock(DataFileCompactor.class);
+        when(compactor.compactSingleLevel(anyList(), anyInt())).thenAnswer(invocation -> {
+            compactedFiles.addAll(invocation.getArgument(0));
+            taskDone.countDown();
+            return true;
+        });
+        when(compactor.getDataFileCollection()).thenReturn(fileCollection);
+
+        coordinator.submitCompactionTasks(ID_TO_HASH_CHUNK, () -> compactor, consolidationConfig);
+
+        assertTrue(taskDone.await(2, TimeUnit.SECONDS), "Consolidation task should complete");
+
+        // Only level 1 files should be consolidated (12 files)
+        assertEquals(12, compactedFiles.size(), "Only level 1 files should be consolidated");
+        for (final DataFileReader f : compactedFiles) {
+            assertEquals(1, f.getMetadata().getCompactionLevel(), "All consolidated files should be level 1");
+        }
+    }
+
     // ========================================================================
     // absorbIntoGroup tests
     // ========================================================================
@@ -641,6 +709,30 @@ void testCompactionTaskResetsCompactionInProgressFlagOnFailure() throws Interrup
         verify(file).resetCompactionInProgress();
     }
 
+    @Test
+    void testCompactionTaskDoesNotResetFlagOnSuccess() throws InterruptedException, IOException {
+        // After successful compaction, the flag must stay true — resetting it would
+        // allow a concurrent task's CAS to succeed on a file that's already been deleted.
+        final DataFileReader file = mockFileReader(1, 0, 100, 1000);
+
+        final DataFileCollection fileCollection = mock(DataFileCollection.class);
+        when(fileCollection.getAllCompletedFiles()).thenReturn(List.of(file));
+
+        publishScanStats(ID_TO_HASH_CHUNK, buildStats(new StatsEntry(file, 20)));
+
+        final DataFileCompactor compactor = mock(DataFileCompactor.class);
+        when(compactor.compactSingleLevel(anyList(), anyInt())).thenReturn(true);
+        when(compactor.getDataFileCollection()).thenReturn(fileCollection);
+
+        coordinator.submitCompactionTasks(ID_TO_HASH_CHUNK, () -> compactor, config);
+
+        coordinator.awaitForCurrentCompactionsToComplete(2000);
+
+        // Flag was set but must NOT be reset after success
+        verify(file).setCompactionInProgress();
+        verify(file, never()).resetCompactionInProgress();
+    }
+
     @Test
     void testIsCompactionRunningDetectsGarbageCompactionTask() throws InterruptedException, IOException {
         final DataFileReader level0File = mockFileReader(1, 0, 100, 1000);
@@ -682,7 +774,7 @@ void testIsCompactionRunningDetectsConsolidationTask() throws InterruptedExcepti
         final List<DataFileReader> smallFiles = new ArrayList<>();
         final List<StatsEntry> statsEntries = new ArrayList<>();
         for (int i = 1; i <= 12; i++) {
-            final DataFileReader f = mockFileReader(i, 0, 100, 5 * 1024 * 1024);
+            final DataFileReader f = mockFileReader(i, 1, 100, 5 * 1024 * 1024);
             smallFiles.add(f);
             statsEntries.add(new StatsEntry(f, 100)); // all alive → d/a = 0.0
         }
@@ -757,6 +849,62 @@ void testIsCompactionRunningDoesNotCrossStores() throws InterruptedException, IO
         coordinator.awaitForCurrentCompactionsToComplete(2000);
     }
 
+    @Test
+    void testSetCompactionInProgressCASPreventsDoubleAssignment() throws InterruptedException, IOException {
+        // A file that appears in both a garbage task and a consolidation task from different
+        // submitCompactionTasks calls. The CAS on setCompactionInProgress ensures only the
+        // first task to execute claims the file.
+        final DataFileReader sharedFile = mockFileReader(1, 1, 100, 5 * 1024 * 1024);
+
+        // Use a real AtomicBoolean to simulate CAS behavior
+        final AtomicBoolean flag = new AtomicBoolean(false);
+        when(sharedFile.setCompactionInProgress()).thenAnswer(_ -> flag.compareAndSet(false, true));
+        when(sharedFile.isCompactionInProgress()).thenAnswer(_ -> flag.get());
+
+        // 20 alive out of 100 → d/a = 4.0 → eligible for garbage compaction
+        publishScanStats(ID_TO_HASH_CHUNK, buildStats(new StatsEntry(sharedFile, 20)));
+
+        final DataFileCollection fileCollection = mock(DataFileCollection.class);
+        when(fileCollection.getAllCompletedFiles()).thenReturn(List.of(sharedFile));
+
+        // First task: grabs the file via CAS
+        final CountDownLatch task1Started = new CountDownLatch(1);
+        final CountDownLatch task1Release = new CountDownLatch(1);
+        final List<DataFileReader> task1Files = new ArrayList<>();
+        final DataFileCompactor compactor1 = mock(DataFileCompactor.class);
+        when(compactor1.compactSingleLevel(anyList(), anyInt())).thenAnswer(invocation -> {
+            task1Files.addAll(invocation.getArgument(0));
+            task1Started.countDown();
+            task1Release.await(2, TimeUnit.SECONDS);
+            return true;
+        });
+        when(compactor1.getDataFileCollection()).thenReturn(fileCollection);
+
+        // Submit first task
+        coordinator.submitCompactionTasks(ID_TO_HASH_CHUNK, () -> compactor1, config);
+        assertTrue(task1Started.await(1, TimeUnit.SECONDS), "First task should start");
+
+        // File is now flagged via CAS — second task should not be able to claim it
+        assertTrue(flag.get(), "File should be flagged after first task starts");
+
+        // Submit second task (simulating a second submitCompactionTasks call)
+        final List<DataFileReader> task2Files = new ArrayList<>();
+        final DataFileCompactor compactor2 = mock(DataFileCompactor.class);
+        when(compactor2.compactSingleLevel(anyList(), anyInt())).thenAnswer(invocation -> {
+            task2Files.addAll(invocation.getArgument(0));
+            return true;
+        });
+        when(compactor2.getDataFileCollection()).thenReturn(fileCollection);
+
+        coordinator.submitCompactionTasks(ID_TO_HASH_CHUNK, () -> compactor2, config);
+        task1Release.countDown();
+        coordinator.awaitForCurrentCompactionsToComplete(2000);
+
+        // First task should have the file, second task should have been filtered out
+        assertEquals(1, task1Files.size(), "First task should have claimed the file");
+        assertTrue(task2Files.isEmpty(), "Second task should not have claimed the file");
+    }
+
     // ========================================================================
     // Helper methods
     // ========================================================================
@@ -809,6 +957,7 @@ private static DataFileReader mockFileReader(
         when(reader.getIndex()).thenReturn(fileIndex);
         when(reader.getMetadata()).thenReturn(metadata);
         when(reader.getSize()).thenReturn(sizeBytes);
+        when(reader.setCompactionInProgress()).thenReturn(true);
         return reader;
     }
 
```
