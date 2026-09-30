# [?] ENT-6631 - upgrade jackson version to get rid of databind vulnerability, keeping jackson-module-kotlin the same

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2022-02-24
Source: https://github.com/corda/corda/commit/9dfdd71c223ed6dc3d2d9fabfb3c9a7c44ecae33
Type: security-commit

## Details
ENT-6631 - upgrade jackson version to get rid of databind vulnerability, keeping jackson-module-kotlin the same

## Patch
### build.gradle
```diff
@@ -63,7 +63,8 @@ buildscript {
     ext.asm_version = '7.1'
     ext.artemis_version = '2.19.1'
     // TODO Upgrade Jackson only when corda is using kotlin 1.3.10
-    ext.jackson_version = '2.9.7'
+    ext.jackson_version = '2.11.1'
+    ext.jackson_kotlin_version = '2.9.7'
     ext.jetty_version = '9.4.19.v20190610'
     ext.jersey_version = '2.25'
     ext.servlet_version = '4.0.1'
```

### client/jackson/build.gradle
```diff
@@ -9,7 +9,9 @@ dependencies {
 
     compile "org.jetbrains.kotlin:kotlin-stdlib-jdk8:$kotlin_version"
     // Jackson and its plugins: parsing to/from JSON and other textual formats.
-    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version"
+    compile("com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version") {
+        exclude module: "jackson-databind"
+    }
     // Yaml is useful for parsing strings to method calls.
     compile "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:$jackson_version"
     // This adds support for java.time types.
```

### samples/irs-demo/cordapp/workflows-irs/build.gradle
```diff
@@ -16,7 +16,7 @@ dependencies {
     cordaCompile project(':core')
     
 
-    compile("com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version")
+    compile("com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version")
     
     // only included to control the `DemoClock` as part of the demo application
     // normally `:node` should not be depended on in any CorDapps
```

### samples/irs-demo/web/build.gradle
```diff
@@ -70,7 +70,7 @@ dependencies {
     }
     compile('org.springframework.boot:spring-boot-starter-log4j2')
     runtimeOnly("org.apache.logging.log4j:log4j-web:$log4j_version")
-    compile("com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version")
+    compile("com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version")
     compile project(":client:rpc")
     compile project(":client:jackson")
     compile project(":finance:workflows")
```

### testing/test-cli/build.gradle
```diff
@@ -6,7 +6,7 @@ dependencies {
     compile "org.jetbrains.kotlin:kotlin-reflect:$kotlin_version"
     compile "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:$jackson_version"
     compile "com.fasterxml.jackson.core:jackson-databind:$jackson_version"
-    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version"
+    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version"
     
     compile "org.junit.jupiter:junit-jupiter-api:${junit_jupiter_version}"
     compile "junit:junit:${junit_version}"
```

### tools/network-builder/build.gradle
```diff
@@ -52,7 +52,7 @@ dependencies {
     compile "com.typesafe:config:$typesafe_config_version"
     compile "com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:$jackson_version"
     compile "com.fasterxml.jackson.core:jackson-databind:$jackson_version"
-    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_version"
+    compile "com.fasterxml.jackson.module:jackson-module-kotlin:$jackson_kotlin_version"
     compile "info.picocli:picocli:$picocli_version"
 
     // TornadoFX: A lightweight Kotlin framework for working with JavaFX UI's.
```
