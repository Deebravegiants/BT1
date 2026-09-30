# [?] fuzz: cap the crash store at 10k inputs

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-08-29
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/9911d236ace906e8380cf6677f766a8b73c9867a
Type: security-commit

## Details
fuzz: cap the crash store at 10k inputs

Oldest inputs get dropped past the cap.

## Patch
### fuzz/corpora.sh
```diff
@@ -8,7 +8,8 @@
 #   seed     Copy a target's stored corpus into fuzz/corpus.
 #   refresh  Replace each stored corpus with the one under INCOMING_CORPORA, add
 #            crash inputs under INCOMING_CRASHES to the fuzz_crashes store and
-#            drop targets not listed in TARGETS_FILE.
+#            drop targets not listed in TARGETS_FILE. The crash store is
+#            then trimmed to MAX_STORED_CRASHES.
 #   replay   Run every input in the fuzz_crashes store under QA_DIR against
 #            its target and fail if any of them still crashes.
 #   push     CI only, not meant to be run locally. Commit and push to
@@ -22,6 +23,10 @@ set -euo pipefail
 
 usage="Usage: $0 {seed QA_DIR TARGET | refresh INCOMING_CORPORA INCOMING_CRASHES TARGETS_FILE | replay QA_DIR | push}"
 
+# Upper bound on inputs kept in the crash store, oldest dropped first.
+# 40MB is the limit, because libFuzzer default max input size is 4KB.
+readonly MAX_STORED_CRASHES=10000
+
 seed() {
   local qa="${1:?$usage}" target="${2:?$usage}"
   local corpus
@@ -31,6 +36,27 @@ seed() {
     find "$qa/fuzz_corpora/$target" -maxdepth 1 -type f -exec cp -t "$corpus/" {} +
   fi
 }
+# Trim the crash store to MAX_STORED_CRASHES, oldest first.
+maybe_prune_old_crashes() {
+  local total excess file oldest_first
+
+  total=$(find fuzz_crashes -type f | wc -l)
+  excess=$((total - MAX_STORED_CRASHES))
+  [ "$excess" -gt 0 ] || return 0
+  echo "Crash store holds $total inputs, dropping $excess oldest"
+
+  # Get files by the age of first presence in commit, ascending.
+  oldest_first=$(git log --reverse --diff-filter=A --format='' --name-only \
+                     -- fuzz_crashes | awk 'NF && !seen[$0]++')
+
+  while IFS= read -r file; do
+    [ "$excess" -gt 0 ] || break
+    [ -f "$file" ] || continue
+    rm -f -- "$file"
+    excess=$((excess - 1))
+  done <<< "$oldest_first"
+  find fuzz_crashes -mindepth 1 -type d -empty -delete
+}
 
 refresh() {
   local corpora="${1:?$usage}" crashes="${2:?$usage}" targets_file="${3:?$usage}"
@@ -63,6 +89,7 @@ refresh() {
     name=$(basename "$dir")
     grep -qx "$name" "$targets_file" || rm -rf "$dir"
   done
+  maybe_prune_old_crashes
 }
 
 replay() {
```
