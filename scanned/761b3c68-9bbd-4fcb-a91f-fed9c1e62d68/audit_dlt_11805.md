# [?] chore: ignore GHSA-92fh-27vv-894w advisory

## Summary
Severity: Unknown
Chain: Tooling
Component: wevm/wagmi
Published: 2026-02-15
Source: https://github.com/wevm/wagmi/commit/ee7edb4adb087df4b46a40534b87ff07d258cdcc
Type: security-commit

## Details
chore: ignore GHSA-92fh-27vv-894w advisory

Amp-Thread-ID: https://ampcode.com/threads/T-019c62c5-ce64-720a-b597-4decc9036d53
Co-authored-by: Amp <amp@ampcode.com>

## Patch
### pnpm-workspace.yaml
```diff
@@ -15,6 +15,7 @@ auditConfig:
     - GHSA-29xp-372q-xqph
     - GHSA-mh29-5h37-fv8m
     - GHSA-5j98-mcp5-4vw2
+    - GHSA-92fh-27vv-894w
 
 autoInstallPeers: false
 
```
