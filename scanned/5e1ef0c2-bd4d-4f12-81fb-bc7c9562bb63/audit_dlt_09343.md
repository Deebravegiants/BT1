# [?] chore: ignore lodash audit vulnerabilities from @pimlico/alto>bull (#4444)

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/viem
Published: 2026-04-02
Source: https://github.com/wevm/viem/commit/d554ad3fd0583f13a999f672052c3a5a88548dd7
Type: security-commit

## Details
chore: ignore lodash audit vulnerabilities from @pimlico/alto>bull (#4444)

Co-authored-by: tmm <6759464+tmm@users.noreply.github.com>

## Patch
### pnpm-workspace.yaml
```diff
@@ -10,7 +10,9 @@ auditConfig:
     - GHSA-ffrw-9mx8-89p8
     - GHSA-mh29-5h37-fv8m
     - GHSA-7r86-cg39-jmmj
-    - GHSA-23c5-xmqv-rm74 
+    - GHSA-23c5-xmqv-rm74
+    - GHSA-r5fr-rjxr-66jc
+    - GHSA-f23m-r3pf-42rh
 
 catalog:
   '@types/react': ^19
```
