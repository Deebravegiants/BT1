# [?] release(cp): chore: ignore minimatch ReDoS advisory (GHSA-3ppc-4f35-3m26) (#40221)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-19
Source: https://github.com/MetaMask/metamask-extension/commit/c18f899a6eb87854244adeaa23ba1b41dc25bec7
Type: security-commit

## Details
release(cp): chore: ignore minimatch ReDoS advisory (GHSA-3ppc-4f35-3m26) (#40221)

## Patch
### .yarnrc.yml
```diff
@@ -43,6 +43,11 @@ npmAuditIgnoreAdvisories:
   # URL: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
   - 1113214
 
+  # Issue: minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern
+  # Only affects dev/build-time dependencies (eslint-plugin-n, glob) — not shipped to users.
+  # URL: https://github.com/advisories/GHSA-3ppc-4f35-3m26
+  - 1113296
+
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
```
