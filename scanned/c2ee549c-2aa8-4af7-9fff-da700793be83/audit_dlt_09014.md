# [?] [CORDA-2189] Fix non deterministic manifest file timestamp (#4301)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2018-11-26
Source: https://github.com/corda/corda/commit/88ee343e9561ead81fed07785d39b80d51f83085
Type: security-commit

## Details
[CORDA-2189] Fix non deterministic manifest file timestamp (#4301)

## Patch
### testing/node-driver/src/main/kotlin/net/corda/testing/node/internal/TestCordappsUtils.kt
```diff
@@ -4,9 +4,11 @@ import io.github.classgraph.ClassGraph
 import net.corda.core.internal.outputStream
 import net.corda.node.internal.cordapp.createTestManifest
 import net.corda.testing.node.TestCordapp
+import java.io.BufferedOutputStream
 import java.nio.file.Path
 import java.nio.file.attribute.FileTime
 import java.time.Instant
+import java.util.jar.JarFile
 import java.util.jar.JarOutputStream
 import java.util.zip.ZipEntry
 import kotlin.reflect.KClass
@@ -65,8 +67,13 @@ fun TestCordappImpl.packageAsJar(file: Path) {
 
     scanResult.use {
         val manifest = createTestManifest(name, title, version, vendor, targetVersion)
-        JarOutputStream(file.outputStream(), manifest).use { jos ->
+        JarOutputStream(file.outputStream()).use { jos ->
             val time = FileTime.from(Instant.EPOCH)
+            val manifestEntry = ZipEntry(JarFile.MANIFEST_NAME).setCreationTime(time).setLastAccessTime(time).setLastModifiedTime(time)
+            jos.putNextEntry(manifestEntry)
+            manifest.write(BufferedOutputStream(jos))
+            jos.closeEntry()
+
             // The same resource may be found in different locations (this will happen when running from gradle) so just
             // pick the first one found.
             scanResult.allResources.asMap().forEach { path, resourceList ->
```
