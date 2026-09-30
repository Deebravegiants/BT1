# [?] Add fix for CVE-2024-7254 (#8647)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2024-09-26
Source: https://github.com/Consensys-Incorporated/teku/commit/b91c43237fe5eae29ddcb772b1cf3688fc3e8d56
Type: security-commit

## Details
Add fix for CVE-2024-7254 (#8647)

## Patch
### CHANGELOG.md
```diff
@@ -16,6 +16,7 @@
 - Renamed metrics `validator_attestation_publication_delay`,`validator_block_publication_delay` and `beacon_block_import_delay_counter` to include the suffix `_total` added by the current version of prometheus.
 - Updated bootnodes for Holesky network
 - Added new `--p2p-flood-publish-enabled` parameter to control whenever flood publishing behaviour is enabled (applies to all subnets). Previous teku versions always had this behaviour enabled. Default is `true`.
+- Add a fix for [CVE-2024-7254](https://avd.aquasec.com/nvd/2024/cve-2024-7254/)
 
 ### Bug Fixes
  - removed a warning from logs about non blinded blocks being requested (#8562)
```

### gradle/versions.gradle
```diff
@@ -32,7 +32,7 @@ dependencyManagement {
       entry 'javalin-rendering'
     }
 
-    dependency 'io.libp2p:jvm-libp2p:1.1.1-RELEASE'
+    dependency 'io.libp2p:jvm-libp2p:1.2.0-RELEASE'
     dependency 'tech.pegasys:jblst:0.3.12'
     dependency 'tech.pegasys:jc-kzg-4844:1.0.0'
 
```
