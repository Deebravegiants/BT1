# [?] ENT-6336,ENT-6960 - upgrade snakeyaml to address security vulnerabilities

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2023-04-06
Source: https://github.com/corda/corda/commit/95c4a18352c097f8c885b24cfdcb5e1abc915d06
Type: security-commit

## Details
ENT-6336,ENT-6960 - upgrade snakeyaml to address security vulnerabilities

## Patch
### build.gradle
```diff
@@ -63,7 +63,8 @@ buildscript {
     ext.asm_version = '7.1'
     ext.artemis_version = '2.6.2'
     // TODO Upgrade to Jackson 2.10+ only when corda is using kotlin 1.3.10
-    ext.jackson_version = '2.9.8'
+    ext.jackson_version = '2.13.3'
+    ext.jackson_kotlin_version = '2.9.7'
     ext.jetty_version = '9.4.19.v20190610'
     ext.jersey_version = '2.25'
     ext.servlet_version = '4.0.1'
@@ -259,7 +260,7 @@ allprojects {
     apply plugin: 'org.owasp.dependencycheck'
     apply plugin: 'kotlin-allopen'
     apply plugin: 'org.sonarqube'
-
+    
     allOpen {
         annotations(
                 "javax.persistence.Entity",
@@ -417,6 +418,10 @@ allprojects {
                             details.useVersion netty_version
                         }
                     }
+
+                    if (details.requested.group == 'org.yaml' && details.requested.name == 'snakeyaml') {
+                        details.useVersion snake_yaml_version
+                    }
                 }
             }
         }
```

### client/jackson/build.gradle
```diff
@@ -9,7 +9,7 @@ dependencies {
 
     compile "org.jetbrains.kotlin:kotlin-stdlib-jdk8:$kotlin_version"
     // Jackson and its plugins: parsing to/from JSON and other textual formats.
-    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version"
+    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version"
     // Yaml is useful for parsing strings to method calls.
     compile "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:$jackson_version"
     // This adds support for java.time types.
```

### constants.properties
```diff
@@ -25,7 +25,7 @@ disruptorVersion=3.4.2
 typesafeConfigVersion=1.3.4
 jsr305Version=3.0.2
 artifactoryPluginVersion=4.7.3
-snakeYamlVersion=1.19
+snakeYamlVersion=1.33
 caffeineVersion=2.7.0
 metricsVersion=4.1.0
 metricsNewRelicVersion=1.1.1
```

### settings.gradle
```diff
@@ -82,10 +82,10 @@ include 'tools:checkpoint-agent'
 include 'samples:attachment-demo:contracts'
 include 'samples:attachment-demo:workflows'
 include 'samples:trader-demo:workflows-trader'
-include 'samples:irs-demo'
-include 'samples:irs-demo:cordapp:contracts-irs'
-include 'samples:irs-demo:cordapp:workflows-irs'
-include 'samples:irs-demo:web'
+// include 'samples:irs-demo'
+// include 'samples:irs-demo:cordapp:contracts-irs'
+// include 'samples:irs-demo:cordapp:workflows-irs'
+// include 'samples:irs-demo:web'
 include 'samples:simm-valuation-demo'
 include 'samples:simm-valuation-demo:flows'
 include 'samples:simm-valuation-demo:contracts-states'
```
