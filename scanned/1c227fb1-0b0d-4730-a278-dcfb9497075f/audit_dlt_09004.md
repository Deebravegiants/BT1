# [?] Security vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2024-01-12
Source: https://github.com/corda/corda/commit/07a2d98d0b71ddc50d2dbef81118c372f0103ba7
Type: security-commit

## Details
Security vulnerabilities

## Patch
### build.gradle
```diff
@@ -65,7 +65,7 @@ buildscript {
     // TODO Upgrade Jackson only when corda is using kotlin 1.3.10
     ext.jackson_version = '2.13.5'
     ext.jackson_kotlin_version = '2.9.7'
-    ext.jetty_version = '9.4.52.v20230823'
+    ext.jetty_version = '9.4.53.v20231009'
     ext.jersey_version = '2.25'
     ext.servlet_version = '4.0.1'
     ext.assertj_version = '3.12.2'
```
