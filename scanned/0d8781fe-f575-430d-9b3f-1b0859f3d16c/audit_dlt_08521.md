# [?] workbench: fix a race condition on Nomad job startup failure

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/cardano-node
Published: 2023-05-23
Source: https://github.com/IntersectMBO/cardano-node/commit/2d9c51a56fc33b81d9c175cc6c1f715541517579
Type: security-commit

## Details
workbench: fix a race condition on Nomad job startup failure

## Patch
### nix/workbench/nomad.sh
```diff
@@ -1336,21 +1336,24 @@ EOF
           then
             return_code=1
             msg "$(red "FATAL: One or more Nomad Evaluations failed!")"
-            msg "$(yellow "See logs on: $(ls "${job_file}.run/evaluation.*.error.json")")"
+            # Due to race conditions the *.error file may not be preset.
+            msg "$(yellow "See logs on: $(ls "${job_file}.run/evaluation.*.error.json" 2>/dev/null || true)")"
           fi
           # Any failed allocations?
           if test -f "${job_file}.run/allocations.error"
           then
             return_code=1
             msg "$(red "FATAL: One or more Nomad Allocations failed!")"
-            msg "$(yellow "See logs on: $(ls "${job_file}.run/allocation.*.error.json")")"
+            # Due to race conditions the *.error file may not be preset.
+            msg "$(yellow "See logs on: $(ls "${job_file}.run/allocation.*.error.json" 2>/dev/null || true)")"
           fi
           # Any allocation's tasks failed?
           if test -f "${job_file}.run/tasks.*.error"
           then
             return_code=1
             msg "$(red "FATAL: One or more Nomad Allocation Tasks failed!")"
-            msg "$(yellow "See logs on: $(ls "${job_file}.run/task.*.error.json")")"
+            # Due to race conditions the *.error file may not be preset.
+            msg "$(yellow "See logs on: $(ls "${job_file}.run/task.*.error.json" 2>/dev/null || true)")"
           fi
           # Any other generic error?
           if test -f "${job_file}.run/job.error"
@@ -1372,7 +1375,7 @@ EOF
           then
             "${msgoff}" || msg "$(red "FATAL: Command \"nomad eval list\" failed")"
             "${msgoff}" || msg "${job_evals_result}"
-            # Fatal job error!
+            # Send fatal job error signal after printing this error's messages!
             touch "${job_file}.run/job.error"
             return 1
           fi
@@ -1407,9 +1410,9 @@ EOF
             # Wait for all processes to finish or kill them if at least one fails!
             if ! wait_fail_any "${jobs_array[@]}" || test -f "${job_file}.run/evaluations.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               "${msgoff}" || msg "$(red "Exiting monitor of Nomad Evaluations [${evals_array[@]}] due to errors")"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             else
               # If nobody else failed!
@@ -1433,7 +1436,7 @@ EOF
           then
             "${msgoff}" || msg "$(red "FATAL: Command \"nomad job allocs\" failed")"
             "${msgoff}" || msg "${job_allocs_result}"
-            # Fatal job error!
+            # Send fatal job error signal after printing this error's messages!
             touch "${job_file}.run/job.error"
             return 1
           fi
@@ -1468,9 +1471,9 @@ EOF
             # Wait for all processes to finish or kill them if at least one fails!
             if ! wait_fail_any "${jobs_array[@]}" || test -f "${job_file}.run/allocations.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               "${msgoff}" || msg "$(red "Exiting monitor of Nomad Allocations [${allocs_array[@]}] due to errors")"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             else
               # If nobody else failed!
@@ -1495,8 +1498,8 @@ EOF
           then
             "${msgoff}" || msg "$(red "FATAL: Command \"nomad alloc status\" failed")"
             "${msgoff}" || msg "${alloc_status_result}"
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
+            # Send fatal job error signal after printing this error's messages!
+            touch "${job_file}.run/job.error"
             return 1
           fi
           # If no tasks start all over again
@@ -1530,9 +1533,9 @@ EOF
             # Wait for all processes to finish or kill them if at least one fails!
             if ! wait_fail_any "${jobs_array[@]}" || test -f "${job_file}.run/tasks.${alloc_id}.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               "${msgoff}" || msg "$(red "Exiting monitor of Nomad Tasks [${tasks_array[@]}] due to errors")"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             else
               # If nobody else failed!
@@ -1557,8 +1560,8 @@ EOF
           then
             "${msgoff}" || msg "$(red "FATAL: Command \"nomad eval status\" failed")"
             "${msgoff}" || msg "${status_response}"
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
+            # Send fatal job error signal after printing this error's messages!
+            touch "${job_file}.run/job.error"
             return 1
           else
             if echo "${status_response}" | grep --quiet "^Placement Failures = true"
@@ -1585,7 +1588,7 @@ EOF
             then
               "${msgoff}" || msg "$(red "FATAL: Command \"nomad eval status\" failed")"
               "${msgoff}" || msg "${status_response}"
-              # Fatal job error!
+              # Send fatal job error signal after printing this error's messages!
               touch "${job_file}.run/job.error"
               return 1
             fi
@@ -1614,24 +1617,26 @@ EOF
             # Only an evaluation specific error if the loop was not stopped!
             if ! test -f "${job_file}.run/job.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               # Store the error response that ended the loop!
               echo "${status_response}" > "${job_file}.run/evaluation.${eval_id}.error.json"
+              # Show this error messages.
               "${msgoff}" || msg "$(red "FATAL: Nomad Evaluation \"${eval_id}\" failed")"
               "${msgoff}" || msg "${status_response}"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             fi
           else
             # This can't be obtained from the json and happens even if "complete"!
             local placement_response
             if ! placement_response=$(wb_nomad job check-eval-id-placement-failures "${job_file}" "${job_name}" "${eval_id}" "${msgoff}")
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               # Store the error response that ended the loop!
               echo "${status_response}" > "${job_file}.run/evaluation.${eval_id}.error.json"
+              # Show this error messages.
               "${msgoff}" || msg "${placement_response}"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             else
               # Store the response that made it final!
@@ -1656,7 +1661,7 @@ EOF
             then
               "${msgoff}" || msg "$(red "FATAL: Command \"nomad deployment status\" failed")"
               "${msgoff}" || msg "${status_response}"
-              # Fatal job error!
+              # Send fatal job error signal after printing this error's messages!
               touch "${job_file}.run/job.error"
               return 1
             fi
@@ -1703,7 +1708,7 @@ EOF
             then
               "${msgoff}" || msg "$(red "FATAL: Command \"nomad alloc status\" failed")"
               "${msgoff}" || msg "${status_response}"
-              # Fatal job error!
+              # Send fatal job error signal after printing this error's messages!
               touch "${job_file}.run/job.error"
               return 1
             fi
@@ -1733,8 +1738,6 @@ EOF
             # Only an allocation specific error if the loop was not stopped!
             if ! test -f "${job_file}.run/job.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               # Store the error response that ended the loop!
               echo "${status_response}" > "${job_file}.run/allocation.${alloc_id}.error.json"
               msg "$(red "FATAL: Nomad allocation \"${alloc_id}\" failed")"
@@ -1747,6 +1750,8 @@ EOF
               msg "$(yellow "INFO: Nomad allocation \"${alloc_id}\" entrypoint stderr:")"
               nomad alloc logs -verbose -stderr "${alloc_id}" > "${job_file}.run/allocation.${alloc_id}.stderr"
               cat "${job_file}.run/allocation.${alloc_id}.stderr"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             fi
           else
@@ -1778,7 +1783,7 @@ EOF
             then
               "${msgoff}" || msg "$(red "FATAL: Command \"nomad alloc status\" failed")"
               "${msgoff}" || msg "${status_response}"
-              # Fatal job error!
+              # Send fatal job error signal after printing this error's messages!
               touch "${job_file}.run/job.error"
               return 1
             fi
@@ -1793,13 +1798,14 @@ EOF
             # Only a task specific error if the loop was not stopped!
             if ! test -f "${job_file}.run/job.error"
             then
-              # Fatal job error!
-              touch "${job_file}.run/job.error"
               # Store the error response that ended the loop!
               # Remove the entire Job (mayus!!!) description from the Task's log.
               echo "${status_response}" | jq '.Job = null' > "${job_file}.run/task.${task_name}.error.json"
+              # Show this error messages.
               "${msgoff}" || msg "$(red "FATAL: Nomad Task \"${task_name}\" failed")"
               "${msgoff}" || msg "$(echo ${status_response} | jq .TaskStates.\"${task_name}\")"
+              # Send fatal job error signal after printing this error's messages!
+              touch "${job_file}.run/job.error"
               return 1
             fi
           else
```
