# [?] Fix race condition in PCES file copy. (#9890)

## Summary
Severity: Unknown
Chain: Hedera
Component: hiero-ledger/hiero-consensus-node
Published: 2023-11-15
Source: https://github.com/hiero-ledger/hiero-consensus-node/commit/f00aa3c43b829f82b6d19cfcdc7fbeb0dce6872f
Type: security-commit

## Details
Fix race condition in PCES file copy. (#9890)

Signed-off-by: Cody Littley <cody@swirldslabs.com>

## Patch
### platform-sdk/swirlds-platform-core/src/main/java/com/swirlds/platform/state/signed/PreconsensusEventFileRenamed.java
```diff
@@ -0,0 +1,34 @@
+/*
+ * Copyright (C) 2023 Hedera Hashgraph, LLC
+ *
+ * Licensed under the Apache License, Version 2.0 (the "License");
+ * you may not use this file except in compliance with the License.
+ * You may obtain a copy of the License at
+ *
+ *      http://www.apache.org/licenses/LICENSE-2.0
+ *
+ * Unless required by applicable law or agreed to in writing, software
+ * distributed under the License is distributed on an "AS IS" BASIS,
+ * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+ * See the License for the specific language governing permissions and
+ * limitations under the License.
+ */
+
+package com.swirlds.platform.state.signed;
+
+import edu.umd.cs.findbugs.annotations.NonNull;
+
+/**
+ * This exception is thrown when a preconsensus event file is renamed, which prevents a preconsensus event file from
+ * being copied.
+ */
+public class PreconsensusEventFileRenamed extends RuntimeException {
+
+    /**
+     * Constructor.
+     * @param cause the cause
+     */
+    public PreconsensusEventFileRenamed(@NonNull final Throwable cause) {
+        super(cause);
+    }
+}
```

### platform-sdk/swirlds-platform-core/src/main/java/com/swirlds/platform/state/signed/SignedStateFileWriter.java
```diff
@@ -19,6 +19,7 @@
 import static com.swirlds.common.io.utility.FileUtils.executeAndRename;
 import static com.swirlds.common.io.utility.FileUtils.writeAndFlush;
 import static com.swirlds.logging.legacy.LogMarker.EXCEPTION;
+import static com.swirlds.logging.legacy.LogMarker.STARTUP;
 import static com.swirlds.logging.legacy.LogMarker.STATE_TO_DISK;
 import static com.swirlds.platform.config.internal.PlatformConfigUtils.writeSettingsUsed;
 import static com.swirlds.platform.state.signed.SignedStateFileUtils.CURRENT_ADDRESS_BOOK_FILE_NAME;
@@ -63,6 +64,14 @@ public final class SignedStateFileWriter {
 
     private static final Logger logger = LogManager.getLogger(SignedStateFileWriter.class);
 
+    /**
+     * The number of times to attempt to copy the last PCES file. Access to this file is not really coordinated between
+     * this logic and the code responsible for managing PCES file lifecycle, and so there is a small chance that the
+     * file moves when we attempt to make a copy. However, this probability is fairly small, and it is very unlikely
+     * that we will be unable to snatch a copy in time with a few retries.
+     */
+    private static final int COPY_PCES_MAX_RETRIES = 10;
+
     private SignedStateFileWriter() {}
 
     /**
@@ -166,14 +175,40 @@ public static void writeSignedStateFilesToDirectory(
         writeSettingsUsed(directory, platformContext.getConfiguration());
 
         if (selfId != null) {
-            copyPreconsensusEventStreamFiles(
+            copyPreconsensusEventStreamFilesRetryOnFailure(
                     platformContext,
                     selfId,
                     directory,
                     signedState.getState().getPlatformState().getPlatformData().getMinimumGenerationNonAncient());
         }
     }
 
+    private static void copyPreconsensusEventStreamFilesRetryOnFailure(
+            @NonNull final PlatformContext platformContext,
+            @NonNull final NodeId selfId,
+            @NonNull final Path destinationDirectory,
+            final long minimumGenerationNonAncient)
+            throws IOException {
+
+        int triesRemaining = COPY_PCES_MAX_RETRIES;
+        while (triesRemaining > 0) {
+            triesRemaining--;
+            try {
+                copyPreconsensusEventStreamFiles(
+                        platformContext, selfId, destinationDirectory, minimumGenerationNonAncient);
+                return;
+            } catch (final PreconsensusEventFileRenamed e) {
+                if (triesRemaining == 0) {
+                    logger.error(
+                            EXCEPTION.getMarker(),
+                            "Unable to copy the last PCES file after {} retries. "
+                                    + "PCES files will not be written into the state.",
+                            COPY_PCES_MAX_RETRIES);
+                }
+            }
+        }
+    }
+
     /**
      * Copy preconsensus event files into the signed state directory. These files are necessary for the platform to use
      * the state file as a starting point. Note: starting a node using the PCES files in the state directory does not
@@ -345,15 +380,20 @@ private static void copyPreconsensusFileList(
                 "Copying {} preconsensus event files to state snapshot directory",
                 filesToCopy.size());
 
+        // The last file might be in the process of being written, so we need to do a deep copy of it.
+        // Unlike the other files we are going to copy which have a long lifespan and are expected to
+        // be stable, the last file is actively in flux. It's possible that the last file will be
+        // renamed by the time we get to it, which may cause this copy operation to fail. Attempt
+        // to copy this file first, so that if we fail we can abort and retry without other side
+        // effects.
+        deepCopyPreconsensusFile(filesToCopy.get(filesToCopy.size() - 1), pcesDestination);
+
         // Although the last file may be currently in the process of being written, all previous files will
         // be closed and immutable and so it's safe to hard link them.
         for (int index = 0; index < filesToCopy.size() - 1; index++) {
             hardLinkPreconsensusFile(filesToCopy.get(index), pcesDestination);
         }
 
-        // The last file might be in the process of being written, so we need to do a deep copy of it.
-        deepCopyPreconsensusFile(filesToCopy.get(filesToCopy.size() - 1), pcesDestination);
-
         logger.info(
                 STATE_TO_DISK.getMarker(),
                 "Finished copying {} preconsensus event files to state snapshot directory",
@@ -382,7 +422,7 @@ private static void hardLinkPreconsensusFile(
     }
 
     /**
-     * Deep copy a PCES file.
+     * Attempt to deep copy a PCES file.
      *
      * @param file            the file to copy
      * @param pcesDestination the directory where the file should be copied into
@@ -392,7 +432,8 @@ private static void deepCopyPreconsensusFile(
         try {
             Files.copy(file.getPath(), pcesDestination.resolve(file.getFileName()));
         } catch (final IOException e) {
-            logger.error(EXCEPTION.getMarker(), "Exception when copying preconsensus event file", e);
+            logger.info(STARTUP.getMarker(), "unable to copy last PCES file (file was likely renamed), will retry");
+            throw new PreconsensusEventFileRenamed(e);
         }
     }
 
```
