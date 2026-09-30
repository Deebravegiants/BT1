# [?] test(a3p): fail z:acceptance fast on follower consensus failure

## Summary
Severity: Unknown
Chain: Agoric
Component: Agoric/agoric-sdk
Published: 2026-06-16
Source: https://github.com/Agoric/agoric-sdk/commit/80d6c72605c465b2a5ad404268a07261871f87b9
Type: security-commit

## Details
test(a3p): fail z:acceptance fast on follower consensus failure

A fatal SwingSet init / consensus failure in the state-sync follower
stops its consensus reactor but leaves the cometbft process running
(still doing peer exchange), so the runner never exits. Because the
crash detection relied on the EXIT trap writing an "exit code" message,
a process that never exits never reports failure: wait-for-follower.mjs
blocks forever on a "ready" that will never come, and the test hangs
until the CI job is force-cancelled (~25 min of zombie pex spam).

Observed on the Endo sync branch, where the follower hit:

  CONSENSUS FAILURE!!! err="cannot initialize Controller: Error:
  package.json at ".../a3p-integration/package.json" must have a
  "name" field"

Watch the follower's output stream and, on a consensus failure, write a
non-"ready" message to the rendezvous file so wait-for-follower.mjs
unblocks and the test fails within seconds instead of timing out. Scope
the detection to the follower's output rather than a blanket log grep so
the deliberate consensus failure in n:upgrade-next is not caught. Set
pipefail so the runner's real exit status still propagates through the
new pipe and the existing post-test "exit code 0" check is preserved.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### a3p-integration/proposals/z:acceptance/host/before-test-run.sh
```diff
@@ -22,6 +22,9 @@ main() {
 
 start_follower() {
   trap 'echo -n "exit code $?" > "$MESSAGE_FILE_PATH"' EXIT
+  # Make the runner's exit status (not the output filter's) propagate through
+  # the pipe below, so a runner that exits non-zero is still reported as such.
+  set -o pipefail
   AG_CHAIN_COSMOS_HOME="$AG_CHAIN_COSMOS_HOME" \
     SDK_SRC="$COMMON_PARENT/$SDK_REPOSITORY_NAME" \
     "$LOADGEN_PATH/runner/bin/loadgen-runner" \
@@ -33,10 +36,30 @@ start_follower() {
     --profile "testnet" \
     --stages "3" \
     --testnet-origin "file://$NETWORK_CONFIG" \
-    --use-state-sync
+    --use-state-sync \
+    2>&1 | fail_fast_on_consensus_failure
   exit
 }
 
+# A fatal SwingSet init / consensus failure stops the follower's consensus
+# reactor but leaves its cometbft process running (still doing peer exchange),
+# so the runner never exits and the EXIT trap above never fires. Without this,
+# the runner never writes a "ready" (or "exit code") message and the acceptance
+# test hangs until the CI job is force-cancelled. Watch the follower's output
+# and, on a consensus failure, write a non-"ready" message so
+# wait-for-follower.mjs unblocks and the test fails immediately.
+fail_fast_on_consensus_failure() {
+  local line
+  while IFS= read -r line; do
+    printf '%s\n' "$line"
+    case $line in
+    *'CONSENSUS FAILURE'*)
+      echo -n "exit code 1" > "$MESSAGE_FILE_PATH"
+      ;;
+    esac
+  done
+}
+
 wait_for_network_config() {
   local network_config
 
```
