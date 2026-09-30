# [?] Fix reported security issue on Netty (#6688)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2023-01-16
Source: https://github.com/Consensys-Incorporated/teku/commit/b489bd0dfc5682d1d09c01e9e3f419b29822cdd2
Type: security-commit

## Details
Fix reported security issue on Netty (#6688)

## Patch
### CHANGELOG.md
```diff
@@ -34,4 +34,5 @@ For information on changes in released versions of Teku, see the [releases page]
 
 ### Bug Fixes
 - Fixed issue which could cause command line options to be parsed incorrectly
-- Fixed issue where the voluntary-exit subcommand did not exit immediately after completion
\ No newline at end of file
+- Fixed issue where the voluntary-exit subcommand did not exit immediately after completion
+- Fixed reported security issue on Netty, updating to version 4.1.87.Final (addressing [CVE-2022-41881](https://avd.aquasec.com/nvd/2022/cve-2022-41881/))
\ No newline at end of file
```

### gradle/versions.gradle
```diff
@@ -63,7 +63,7 @@ dependencyManagement {
     dependency 'io.github.classgraph:classgraph:4.8.154'
     dependency 'com.github.oshi:oshi-core-java11:6.4.0'
 
-    dependencySet(group: 'io.netty', version: '4.1.71.Final') {
+    dependencySet(group: 'io.netty', version: '4.1.87.Final') {
       entry('netty-all') {
         exclude "io.netty:netty-transport-rxtx"
         exclude "org.rxtx:rxtx"
```
