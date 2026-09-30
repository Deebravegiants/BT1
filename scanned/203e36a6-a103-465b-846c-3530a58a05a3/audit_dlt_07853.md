# [?] scan docker images for vulnerabilities (#4253)

## Summary
Severity: Unknown
Chain: Ethereum
Component: Consensys-Incorporated/teku
Published: 2021-08-18
Source: https://github.com/Consensys-Incorporated/teku/commit/b0ba9f1ee277ae57c8ee448399477af76f2caa51
Type: security-commit

## Details
scan docker images for vulnerabilities (#4253)

* scan docker images for vulnerabilities

Signed-off-by: Paul Harris <paul.harris@consensys.net>

## Patch
### .circleci/config.yml
```diff
@@ -139,6 +139,15 @@ jobs:
           command: |
             ./gradlew --no-daemon --parallel checkMavenCoordinateCollisions spotlessCheck
 
+  dockerScan:
+    executor: small_executor
+    steps:
+      - prepare
+      - run:
+          name: "Scan docker images"
+          command: |
+            ./gradlew --no-daemon --parallel dockerScan
+
   unitTests:
     parallelism: 2
     executor: medium_plus_executor
@@ -481,3 +490,13 @@ workflows:
             - docker
             - extractAPISpec
             - spotless
+  nightly:
+    triggers:
+      - schedule:
+          cron: "0 0 * * *"
+          filters:
+            branches:
+              only:
+                - master
+    jobs:
+      - dockerScan
```

### build.gradle
```diff
@@ -419,6 +419,17 @@ task distDocker  {
   }
 }
 
+task dockerScan {
+  doLast {
+    for (def variant in dockerVariants) {
+      exec {
+        executable "sh"
+        args "-c", "docker scan --file docker/${variant}/Dockerfile consensys/teku:develop-${variant} --severity=high"
+      }
+    }
+  }
+}
+
 subprojects {
   tasks.withType(Test) {
     // If GRADLE_MAX_TEST_FORKS is not set, use half the available processors
```
