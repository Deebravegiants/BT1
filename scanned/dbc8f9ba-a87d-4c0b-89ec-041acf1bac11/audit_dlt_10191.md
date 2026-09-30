# [?] .buildkite: Fix CI pipeline race condition

## Summary
Severity: Unknown
Chain: Oasis
Component: oasisprotocol/oasis-core
Published: 2023-06-12
Source: https://github.com/oasisprotocol/oasis-core/commit/dc75e6e2679d911820f176eb456ba65cc3270769
Type: security-commit

## Details
.buildkite: Fix CI pipeline race condition

## Patch
### .buildkite/scripts/common.sh
```diff
@@ -9,21 +9,22 @@ CLEANING_UP=0
 
 # Download an artifact and change its mode
 download_artifact() {
-    local name=$1
-    local dst_dir=$2
+    local name=${1}
+    local dst_dir=${2}
     local mode=${3:-644}
 
     mkdir -p ${ARTIFACTS_CACHE_DIR} ${ARTIFACTS_TMP_DIR} ${dst_dir}
 
-    if [ -f "${ARTIFACTS_CACHE_DIR}/${name}" ] && (echo "$(buildkite-agent artifact shasum ${name})  ${ARTIFACTS_CACHE_DIR}/${name}" | sha1sum -c); then
-        # use artifact from cache
-        cp -f ${ARTIFACTS_CACHE_DIR}/${name} ${dst_dir}/${name}
-    else
-        # download artifact and cache it
+    if [ -f "${ARTIFACTS_CACHE_DIR}/${name}" ]; then
+        # copy artifact from cache
+        cp -f ${ARTIFACTS_CACHE_DIR}/${name} ${ARTIFACTS_TMP_DIR}/${name}
+    fi
+    if [ ! -f "${ARTIFACTS_TMP_DIR}/${name}" ] || ! (echo "$(buildkite-agent artifact shasum ${name})  ${ARTIFACTS_TMP_DIR}/${name}" | sha1sum -c); then
+        # incorrect artifact, download artifact again and cache it if possible
         buildkite-agent artifact download ${name} ${ARTIFACTS_TMP_DIR}/
-        cp -f ${ARTIFACTS_TMP_DIR}/${name} ${dst_dir}/${name}
-        mv -f ${ARTIFACTS_TMP_DIR}/${name} ${ARTIFACTS_CACHE_DIR}/${name}
+        cp -f ${ARTIFACTS_TMP_DIR}/${name} ${ARTIFACTS_CACHE_DIR}/${name} || echo "copying to cache failed"
     fi
+    cp -f ${ARTIFACTS_TMP_DIR}/${name} ${dst_dir}/${name}
     chmod ${mode} ${dst_dir}/${name}
 }
 
```

### .buildkite/scripts/download_e2e_test_artifacts.sh
```diff
@@ -12,6 +12,9 @@ set -euxo pipefail
 
 source .buildkite/scripts/common.sh
 
+# Randomize beginning of downloads to increase hits in CI pipeline cache
+sleep $((RANDOM % 5))
+
 # Oasis node, test runner, remote signer and runtime loader.
 download_artifact oasis-node go/oasis-node 755
 download_artifact oasis-node.test go/oasis-node 755
```
