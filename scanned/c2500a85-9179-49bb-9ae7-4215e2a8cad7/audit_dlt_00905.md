# [?] ENT-14854 assertj version updated to resolve 4.11-CVE-2026-24400 (#8118)

## Summary
Severity: Unknown
Chain: Corda
Component: corda/corda
Published: 2026-02-20
Source: https://github.com/corda/corda/commit/285f714ad45082a008bfbd0997fb5ced5b0e88ff
Type: security-commit

## Details
ENT-14854 assertj version updated to resolve 4.11-CVE-2026-24400 (#8118)

👮🏻👮🏻👮🏻 !!!! DESCRIBE YOUR CHANGES HERE !!!! DO NOT FORGET !!!! 👮🏻👮🏻👮🏻


# PR Checklist:

- [ ] Have you run the unit, integration and smoke tests as described
[here](https://docs.r3.com/testing.html)?
- [ ] If you added public APIs, did you write the JavaDocs/kdocs?
- [ ] If the changes are of interest to application developers, have you
added them to the changelog, and potentially the [release
notes](https://docs.r3.com/release-notes.html)
(`https://docs.r3.com/release-notes.html`)?
- [ ] If you are contributing for the first time, please read the
[contributor agreement](https://docs.r3.com/contributing.html) now and
add a comment to this pull request stating that your PR is in accordance
with the [Developer's Certificate of
Origin](https://docs.r3.com/contributing.html).

Thanks for your code, it's appreciated! :)

## Patch
### common/configuration-parsing/src/test/kotlin/net/corda/common/configuration/parsing/internal/PropertyValidationTest.kt
```diff
@@ -15,14 +15,12 @@ class PropertyValidationTest {
 
         val property = Configuration.Property.Definition.long(key)
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -34,14 +32,12 @@ class PropertyValidationTest {
 
         val property = Configuration.Property.Definition.long(key)
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -53,14 +49,12 @@ class PropertyValidationTest {
 
         val property = Configuration.Property.Definition.long(key).list()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -72,14 +66,12 @@ class PropertyValidationTest {
 
         val property = Configuration.Property.Definition.long(key).list()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -114,14 +106,12 @@ class PropertyValidationTest {
 
         val property = Configuration.Property.Definition.long(key).list().mapValid(::parseMax)
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.BadValue::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.BadValue::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -134,14 +124,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to false).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -154,14 +142,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to 1.2).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -186,14 +172,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to listOf(false, true)).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -206,14 +190,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to listOf(1, 2, 3)).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -226,14 +208,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to 1).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
-
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
@@ -249,14 +229,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to configObject(nestedKey to false)).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.WrongType::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(nestedKey)
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
-            }
+            assertThat(error.keyName).isEqualTo(nestedKey)
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
         }
     }
 
@@ -272,14 +250,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to configObject()).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(nestedKey)
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
-            }
+            assertThat(error.keyName).isEqualTo(nestedKey)
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
         }
     }
 
@@ -295,14 +271,12 @@ class PropertyValidationTest {
 
         val configuration = configObject(key to configObject(nestedKey to null)).toConfig()
 
-        assertThat(property.validate(configuration, Configuration.Options.defaults).errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
+        val errors = property.validate(configuration, Configuration.Options.defaults).errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.MissingValue::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(nestedKey)
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
-            }
+            assertThat(error.keyName).isEqualTo(nestedKey)
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray(), nestedKey)
         }
     }
 
@@ -352,14 +326,12 @@ class PropertyValidationTest {
 
         val result = property.validate(configuration, Configuration.Options.defaults)
 
-        assertThat(result.errors).satisfies { errors ->
-
-            assertThat(errors).hasSize(1)
-            assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.BadValue::class.java) { error ->
+        val errors = result.errors
+        assertThat(errors).hasSize(1)
+        assertThat(errors.first()).isInstanceOfSatisfying(Configuration.Validation.Error.BadValue::class.java) { error ->
 
-                assertThat(error.keyName).isEqualTo(key.split(".").last())
-                assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
-            }
+            assertThat(error.keyName).isEqualTo(key.split(".").last())
+            assertThat(error.path).containsExactly(*key.split(".").toTypedArray())
         }
     }
 
```

### common/configuration-parsing/src/test/kotlin/net/corda/common/configuration/parsing/internal/SchemaTest.kt
```diff
@@ -191,12 +191,10 @@ class SchemaTest {
 
         val descriptionObj = (printedConfiguration as ConfigObject).toConfig()
 
-        assertThat(descriptionObj.getObjectList("prop3")).satisfies { objects ->
+        val objects = descriptionObj.getObjectList("prop3")
+        objects.forEach { obj ->
 
-            objects.forEach { obj ->
-
-                assertThat(obj.toConfig().getString("prop5")).isEqualTo(Configuration.Property.Definition.SENSITIVE_DATA_PLACEHOLDER)
-            }
+            assertThat(obj.toConfig().getString("prop5")).isEqualTo(Configuration.Property.Definition.SENSITIVE_DATA_PLACEHOLDER)
         }
         assertThat(description).doesNotContain(prop5Value)
     }
```

### common/configuration-parsing/src/test/kotlin/net/corda/common/configuration/parsing/internal/SpecificationTest.kt
```diff
@@ -41,15 +41,11 @@ class SpecificationTest {
         val rpcSettings = RpcSettingsSpec.parse(configuration)
 
         assertThat(rpcSettings.isValid).isTrue()
-        assertThat(rpcSettings.value()).satisfies { value ->
-
-            assertThat(value.useSsl).isEqualTo(useSslValue)
-            assertThat(value.addresses).satisfies { addresses ->
-
-                assertThat(addresses.principal).isEqualTo(principalAddressValue)
-                assertThat(addresses.admin).isEqualTo(adminAddressValue)
-            }
-        }
+        val value = rpcSettings.value()
+        assertThat(value.useSsl).isEqualTo(useSslValue)
+        val addresses = value.addresses
+        assertThat(addresses.principal).isEqualTo(principalAddressValue)
+        assertThat(addresses.admin).isEqualTo(adminAddressValue)
     }
 
     @Test(timeout=300_000)
```

### constants.properties
```diff
@@ -55,7 +55,7 @@ jacksonKotlinVersion=2.9.7
 jettyVersion=9.4.57.v20241219
 jerseyVersion=2.47
 servletVersion=4.0.1
-assertjVersion=3.12.2
+assertjVersion=3.27.7
 slf4JVersion=1.7.30
 log4JVersion=2.17.1
 okhttpVersion=3.14.9
```

### core/src/test/kotlin/net/corda/core/internal/PathUtilsTest.kt
```diff
@@ -76,7 +76,7 @@ class PathUtilsTest {
             assertThat(result)
                 .isRegularFile()
                 .hasParent(dir)
-                .hasSameContentAs(source)
+                .hasSameTextualContentAs(source)
         }
     }
 }
\ No newline at end of file
```

### node/src/integration-test/kotlin/net/corda/node/services/network/PersistentNetworkMapCacheTest.kt
```diff
@@ -87,7 +87,7 @@ class PersistentNetworkMapCacheTest {
             nodeInfo
         }
 
-        assertThat(charlieNetMapCache.getNodesByLegalName(DUMMY_NOTARY_NAME)).containsOnlyElementsOf(distServiceNodeInfos)
+        assertThat(charlieNetMapCache.getNodesByLegalName(DUMMY_NOTARY_NAME)).containsExactlyElementsOf(distServiceNodeInfos)
         assertThatIllegalArgumentException()
                 .isThrownBy { charlieNetMapCache.getNodeByLegalName(DUMMY_NOTARY_NAME) }
                 .withMessageContaining(DUMMY_NOTARY_NAME.toString())
```

### node/src/integration-test/kotlin/net/corda/services/messaging/P2PMessagingTest.kt
```diff
@@ -66,7 +66,7 @@ class P2PMessagingTest {
                 break
             }
         }
-        assertThat(participatingNodes).containsOnlyElementsOf(participatingServiceNodes.map { it.services.myInfo })
+        assertThat(participatingNodes).containsExactlyElementsOf(participatingServiceNodes.map { it.services.myInfo })
     }
 
     private fun InProcess.respondWith(message: Any) {
```

### node/src/test/kotlin/net/corda/node/services/config/NodeConfigurationImplTest.kt
```diff
@@ -132,7 +132,7 @@ class NodeConfigurationImplTest {
 
         val errors = configuration.validate()
 
-        assertThat(errors).hasOnlyOneElementSatisfying { error -> error.contains("compatibilityZoneURL") && error.contains("devMode") }
+        assertThat(errors).singleElement().matches { error -> error.contains("compatibilityZoneURL") && error.contains("devMode") }
     }
 
     @Test(timeout=6_000)
@@ -165,7 +165,7 @@ class NodeConfigurationImplTest {
 
         val errors = configuration.validate()
 
-        assertThat(errors).hasOnlyOneElementSatisfying { error -> error.contains("networkServices") && error.contains("devMode") }
+        assertThat(errors).singleElement().matches { error -> error.contains("networkServices") && error.contains("devMode") }
     }
 
     @Test(timeout=6_000)
@@ -179,8 +179,8 @@ class NodeConfigurationImplTest {
 
         val errors = configuration.validate()
 
-        assertThat(errors).hasOnlyOneElementSatisfying { error ->
-            error.contains("Cannot configure both compatibilityZoneUrl and networkServices simultaneously")
+        assertThat(errors).singleElement().matches { error ->
+            error.contains("cannot specify both 'compatibilityZoneUrl' and 'networkServices'")
         }
     }
 
```

### node/src/test/kotlin/net/corda/node/services/vault/VaultQueryTests.kt
```diff
@@ -650,7 +650,7 @@ abstract class VaultQueryTestsBase : VaultQueryParties {
             }
             val sorted = results.states.sortedBy { it.ref.toString() }
             assertThat(results.states).isEqualTo(sorted)
-            assertThat(results.states).allSatisfy { assertThat(consumed).doesNotContain(it.ref.txhash) }
+            results.states.forEach { assertThat(consumed).doesNotContain(it.ref.txhash) }
         }
     }
 
```
