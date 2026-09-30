# [?] Fix update-docusaurus-deps.sh crash on alerts without a patched version (#7906)

## Summary
Severity: Unknown
Chain: Cardano
Component: IntersectMBO/plutus
Published: 2026-08-17
Source: https://github.com/IntersectMBO/plutus/commit/ce080a900f480917d50b4a7b80fa987ac226bd10
Type: security-commit

## Details
Fix update-docusaurus-deps.sh crash on alerts without a patched version (#7906)

## Patch
### scripts/update-docusaurus-deps.sh
```diff
@@ -41,8 +41,11 @@ RAW_ALERTS="$(gh api "repos/${REPO}/dependabot/alerts" --paginate \
 # Picks, per package, the highest first-patched-version across all of its
 # open alerts (a package can have more than one open advisory). Versions are
 # compared component-wise as numbers so that e.g. 3.10.0 sorts above 3.9.0.
+# Alerts with no patched version have a null version; treat those as lowest
+# so any real patched version wins (fully unpatched packages are dropped
+# below).
 ALERTS_JSON="$(jq '
-    def semver: (. / ".") | map(tonumber? // 0);
+    def semver: ((. // "0") / ".") | map(tonumber? // 0);
     group_by(.package) | map(max_by(.version | semver))
 ' <<< "$RAW_ALERTS")"
 
```
