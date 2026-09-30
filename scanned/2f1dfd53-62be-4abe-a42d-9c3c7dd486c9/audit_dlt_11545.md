# [?] Fix race condition when rebuilding proto files. (#813)

## Summary
Severity: Unknown
Chain: EigenDA
Component: Layr-Labs/eigenda
Published: 2024-10-17
Source: https://github.com/Layr-Labs/eigenda/commit/0ee84f9bb6dc92dd42d7b7af50c2716fa00feaf7
Type: security-commit

## Details
Fix race condition when rebuilding proto files. (#813)

Signed-off-by: Cody Littley <cody@eigenlabs.org>

## Patch
### api/builder/clean.sh
```diff
@@ -7,8 +7,19 @@ SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
 
 API_DIR="${SCRIPT_DIR}/.."
 GRPC_DIR="${API_DIR}/grpc"
-find "${GRPC_DIR}" -name '*.pb.go' -type f | xargs rm -rf
+
+if [ -d "${GRPC_DIR}" ]; then
+  # Delete all compiled protobufs
+  find "${GRPC_DIR}" -name '*.pb.go' -type f | xargs rm -rf
+  # Delete all empty directories
+  find "${GRPC_DIR}" -type d -empty -delete
+fi
 
 DISPERSER_DIR="$SCRIPT_DIR/../../disperser"
 DISPERSER_GRPC_DIR="$DISPERSER_DIR/api/grpc"
-find "${DISPERSER_GRPC_DIR}" -name '*.pb.go' -type f | xargs rm -rf
+if [ -d "${DISPERSER_GRPC_DIR}" ]; then
+  # Delete all compiled protobufs
+  find "${DISPERSER_GRPC_DIR}" -name '*.pb.go' -type f | xargs rm -rf
+  # Delete all empty directories
+  find "${DISPERSER_GRPC_DIR}" -type d -empty -delete
+fi
\ No newline at end of file
```
