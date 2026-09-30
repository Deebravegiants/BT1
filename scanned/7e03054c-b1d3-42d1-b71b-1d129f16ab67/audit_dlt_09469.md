# [?] security fix

## Summary
Severity: Unknown
Chain: Bittensor
Component: RaoFoundation/subtensor
Published: 2026-05-20
Source: https://github.com/RaoFoundation/subtensor/commit/300de6b1d3f28cc02c322d3a1689cce7c1e50f31
Type: security-commit

## Details
security fix

## Patch
### .github/workflows/ai-review.yml
```diff
@@ -493,38 +493,35 @@ jobs:
       # Detect any workspace changes Codex made (auto-fix), commit + push them
       # using the resolved token. Codex itself has no token, so this is the
       # only path through which writes reach GitHub.
-      - name: Apply auto-fix from a clean checkout (same-repo PRs only)
+      # ---------------------------------------------------------------------
+      # Auto-fix is split into two steps to keep the push token strictly
+      # separated from any git invocation against the PR-mutated workspace.
+      #
+      # Step A (no token in env):
+      #   Runs `git add`/`git diff`/`git reset` inside the dirty workspace.
+      #   If the PR has poisoned .gitattributes or .git/config (clean filter,
+      #   diff/textconv driver, fsmonitor, gpg helper, etc.), those helpers
+      #   may execute — but there is no credential in environment for them
+      #   to exfiltrate. The output is a binary-safe patch at /tmp/auto-fix.patch.
+      #
+      # Step B (token in env):
+      #   Operates only on /tmp/ai-review-push/, a fresh clone with vanilla
+      #   git config. Never executes git in $github.workspace.
+      # ---------------------------------------------------------------------
+      - name: Extract auto-fix patch (no credentials)
         if: needs.decide.outputs.is_fork == 'false'
         env:
-          HEAD_REF: ${{ needs.decide.outputs.head_ref }}
-          HEAD_SHA: ${{ needs.decide.outputs.head_sha }}
-          PUSH_TOKEN: ${{ steps.token.outputs.token }}
-          REPO: ${{ github.repository }}
           PR_DIRTY: ${{ github.workspace }}
-        # The PR-mutated checkout cannot be trusted with credentialed git
-        # operations: Codex's workspace-write sandbox may have left state in
-        # .git/config or .gitattributes that would cause git to execute helpers
-        # (gpg.program, core.fsmonitor, diff/smudge filters, etc.) with the
-        # token in env. So we:
-        #   1. Generate a binary-safe patch of the auditor's changes using a
-        #      sanitized git invocation (no hooks, no attributes, no gpg).
-        #   2. Clone a fresh trusted copy of the branch to /tmp.
-        #   3. Verify the fresh HEAD matches what the auditor reviewed (no
-        #      surprise commits from the human in the meantime).
-        #   4. Apply the patch and push from the clean checkout.
-        # Token only ever appears in: this step's env (gone with the runner)
-        # and inline -c http.extraheader args (never persisted to disk).
         run: |
           set -euo pipefail
+          rm -f /tmp/auto-fix.patch
           SAFE_GIT_OPTS=(
             -c core.hooksPath=/dev/null
             -c core.attributesFile=/dev/null
             -c core.fsmonitor=false
             -c commit.gpgSign=false
             -c gpg.program=/bin/false
           )
-
-          # 1. Detect + extract auditor changes from the dirty workspace.
           cd "$PR_DIRTY"
           git "${SAFE_GIT_OPTS[@]}" add -A -- ':!auditor-output.json'
           if git "${SAFE_GIT_OPTS[@]}" diff --cached --quiet; then
@@ -536,22 +533,33 @@ jobs:
           git "${SAFE_GIT_OPTS[@]}" diff --cached --binary > /tmp/auto-fix.patch
           git "${SAFE_GIT_OPTS[@]}" reset
 
-          # 2. Fresh trusted clone (token only on the command line).
+      - name: Push auto-fix from clean checkout (token-bearing; never touches dirty workspace)
+        if: needs.decide.outputs.is_fork == 'false'
+        env:
+          HEAD_REF: ${{ needs.decide.outputs.head_ref }}
+          HEAD_SHA: ${{ needs.decide.outputs.head_sha }}
+          PUSH_TOKEN: ${{ steps.token.outputs.token }}
+          REPO: ${{ github.repository }}
+        # Token only ever appears in: this step's env (gone with the runner)
+        # and inline `-c http.*.extraheader` args (never persisted to disk).
+        # No `cd $GITHUB_WORKSPACE`; no git operations in the dirty checkout.
+        run: |
+          set -euo pipefail
+          if [[ ! -s /tmp/auto-fix.patch ]]; then
+            echo "No auto-fix patch to apply."
+            exit 0
+          fi
           TMPDIR=/tmp/ai-review-push
           rm -rf "$TMPDIR"
           git -c "http.https://github.com/.extraheader=AUTHORIZATION: bearer $PUSH_TOKEN" \
             clone --depth=1 -b "$HEAD_REF" \
             "https://github.com/$REPO.git" "$TMPDIR"
-
-          # 3. Verify the fresh HEAD matches what the auditor reviewed.
           cd "$TMPDIR"
           FRESH_SHA="$(git rev-parse HEAD)"
           if [[ "$FRESH_SHA" != "$HEAD_SHA" ]]; then
             echo "::warning::Fresh HEAD $FRESH_SHA != auditor HEAD $HEAD_SHA; branch advanced during review. Refusing to push to avoid clobbering."
             exit 0
           fi
-
-          # 4. Apply, commit, push — all in the clean checkout's vanilla config.
           git config user.name 'subtensor-ai-review[bot]'
           git config user.email 'subtensor-ai-review@users.noreply.github.com'
           git apply --whitespace=nowarn /tmp/auto-fix.patch
```
