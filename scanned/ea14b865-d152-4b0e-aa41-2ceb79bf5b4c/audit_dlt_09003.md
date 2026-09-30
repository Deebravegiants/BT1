# [?] Vulnerability updates

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2024-07-17
Source: https://github.com/corda/corda/commit/f548c8bdd5fccaa918a271ec3e10b6b5f8fb3fda
Type: security-commit

## Details
Vulnerability updates

## Patch
### build.gradle
```diff
@@ -121,7 +121,7 @@ buildscript {
     ext.proguard_version = constants.getProperty('proguardVersion')
     ext.jsch_version = '0.1.55'
     ext.protonj_version = '0.33.0' // Overide Artemis version
-    ext.snappy_version = '0.4'
+    ext.snappy_version = '0.5'
     ext.class_graph_version = constants.getProperty('classgraphVersion')
     ext.jcabi_manifests_version = '1.1'
     ext.picocli_version = '3.9.6'
```

### constants.properties
```diff
@@ -20,7 +20,7 @@ quasarVersion11=0.8.1_r3
 jdkClassifier11=jdk11
 dockerJavaVersion=3.2.5
 proguardVersion=6.1.1
-bouncycastleVersion=1.68
+bouncycastleVersion=1.78.1
 classgraphVersion=4.8.135
 disruptorVersion=3.4.2
 typesafeConfigVersion=1.3.4
```

### core-deterministic/build.gradle
```diff
@@ -45,8 +45,8 @@ dependencies {
 
     // These dependencies will become "runtime" scoped in our published POM.
     // See publish.dependenciesFrom.defaultScope.
-    deterministicLibraries "org.bouncycastle:bcprov-jdk15on:$bouncycastle_version"
-    deterministicLibraries "org.bouncycastle:bcpkix-jdk15on:$bouncycastle_version"
+    deterministicLibraries "org.bouncycastle:bcprov-jdk18on:$bouncycastle_version"
+    deterministicLibraries "org.bouncycastle:bcpkix-jdk18on:$bouncycastle_version"
     deterministicLibraries "net.i2p.crypto:eddsa:$eddsa_version"
 }
 
```

### core/build.gradle
```diff
@@ -72,8 +72,8 @@ dependencies {
     compile "net.i2p.crypto:eddsa:$eddsa_version"
 
     // Bouncy castle support needed for X509 certificate manipulation
-    compile "org.bouncycastle:bcprov-jdk15on:${bouncycastle_version}"
-    compile "org.bouncycastle:bcpkix-jdk15on:${bouncycastle_version}"
+    compile "org.bouncycastle:bcprov-jdk18on:${bouncycastle_version}"
+    compile "org.bouncycastle:bcpkix-jdk18on:${bouncycastle_version}"
 
     // JPA 2.2 annotations.
     compile "javax.persistence:javax.persistence-api:2.2"
```
