# [?] workbench: fix for race condition when fetching nomad alloc tasks

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/cardano-node
Published: 2023-04-06
Source: https://github.com/IntersectMBO/cardano-node/commit/bf39de953783aaee33b318785d7db56f39de8e1d
Type: security-commit

## Details
workbench: fix for race condition when fetching nomad alloc tasks

## Patch
### nix/workbench/backend/nomad.sh
```diff
@@ -2356,7 +2356,7 @@ backend_nomad() {
               if test -z "${tasks_array:-}"
               then
                 sleep 1
-                backend_nomad nomad monitor-alloc-tasks \
+                backend_nomad nomad job monitor-alloc-tasks \
                   "${job_file}" "${job_name}" "${alloc_id}" "${msgoff}"
               else
                 # Interate through allocation's tasks
```
