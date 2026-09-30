# [?] Suppress incorrect trivy warning for CVE-2022-2191 (#5918)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2022-07-12
Source: https://github.com/Consensys-Incorporated/teku/commit/23dd2a4d384ea218ed1780dc4772b186f4835c53
Type: security-commit

## Details
Suppress incorrect trivy warning for CVE-2022-2191 (#5918)

Only applies to Jetty 10+ but initial CVE reported versions incorrectly.

## Patch
### .circleci/config.yml
```diff
@@ -241,7 +241,7 @@ jobs:
             for FILE in $(ls docker)
             do
               docker pull -q "consensys/teku:develop-$FILE"
-              trivy -q image --exit-code 1 --no-progress --severity HIGH,CRITICAL "consensys/teku:develop-$FILE"
+              trivy -q image --exit-code 1 --no-progress --severity HIGH,CRITICAL --ignorefile "gradle/trivyignore.txt" "consensys/teku:develop-$FILE" 
             done
       - notify
 
```

### gradle/trivyignore.txt
```diff
@@ -0,0 +1,3 @@
+# Only applicable to Jetty 10+, not Jetty 9.4 used in Teku.
+# CVE at https://github.com/advisories/GHSA-8mpp-f3f7-xc28 has been updated
+CVE-2022-2191
\ No newline at end of file
```
