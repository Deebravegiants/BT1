# [?] ENT-16320 Upgrading Netty version to address CVE-2026-59903

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2026-08-20
Source: https://github.com/corda/corda/commit/19a7d4bd0a2ac31c9b30f54b15b3dffc7f3c8f4c
Type: security-commit

## Details
ENT-16320 Upgrading Netty version to address CVE-2026-59903

## Patch
### constants.properties
```diff
@@ -54,7 +54,7 @@ assertjVersion=3.27.7
 slf4JVersion=2.0.12
 log4JVersion=2.25.5
 okhttpVersion=4.12.0
-nettyVersion=4.1.136.Final
+nettyVersion=4.1.137.Final
 fileuploadVersion=2.0.0-M1
 kryoVersion=5.5.0
 kryoSerializerVersion=0.43
```
