# [?] fix: Fix stack overflow in CLI tests

## Summary
Severity: Unknown
Chain: Radix
Component: radixdlt/radixdlt-scrypto
Published: 2024-11-08
Source: https://github.com/radixdlt/radixdlt-scrypto/commit/4de0ecf1f1ea276bfd810dedb6072d6f39bfc1de
Type: security-commit

## Details
fix: Fix stack overflow in CLI tests

## Patch
### radix-clis/src/resim/error.rs
```diff
@@ -87,60 +87,157 @@ impl From<Error> for String {
     }
 }
 
+// impl Debug for Error {
+//     fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+//         let address_encoder = AddressBech32Encoder::for_simulator();
+//         match self {
+//             Error::PackageNotFound(package_address) => {
+//                 write!(
+//                     f,
+//                     "PackageNotFound({})",
+//                     package_address.display(&address_encoder)
+//                 )
+//             }
+//             Error::SchemaNotFound(node_id, schema_hash) => {
+//                 write!(
+//                     f,
+//                     "SchemaNotFound({}, {schema_hash:?})",
+//                     node_id.display(&address_encoder)
+//                 )
+//             }
+//             Error::BlueprintNotFound(package_address, message) => {
+//                 write!(
+//                     f,
+//                     "BlueprintNotFound({}, {message})",
+//                     package_address.display(&address_encoder)
+//                 )
+//             }
+//             Error::ComponentNotFound(component_address) => {
+//                 write!(
+//                     f,
+//                     "ComponentNotFound({})",
+//                     component_address.display(&address_encoder)
+//                 )
+//             }
+//             Error::InstanceSchemaNot(component_address, index) => {
+//                 write!(
+//                     f,
+//                     "InstanceSchemaNot({}, {index})",
+//                     component_address.display(&address_encoder)
+//                 )
+//             }
+//             Error::TransactionFailed(runtime_error) => {
+//                 write!(
+//                     f,
+//                     "TransactionFailed({})",
+//                     runtime_error.display(&address_encoder)
+//                 )
+//             }
+//             Error::TransactionRejected(rejection_reason) => {
+//                 write!(
+//                     f,
+//                     "TransactionRejected({})",
+//                     rejection_reason.display(&address_encoder)
+//                 )
+//             }
+//             other => write!(f, "{:?}", other),
+//         }
+//     }
+// }
+
 impl Debug for Error {
-    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
+    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
         let address_encoder = AddressBech32Encoder::for_simulator();
+        let address_encoder = &address_encoder;
         match self {
-            Error::PackageNotFound(package_address) => {
-                write!(
-                    f,
-                    "PackageNotFound({})",
-                    package_address.display(&address_encoder)
-                )
-            }
-            Error::SchemaNotFound(node_id, schema_hash) => {
-                write!(
-                    f,
-                    "SchemaNotFound({}, {schema_hash:?})",
-                    node_id.display(&address_encoder)
-                )
+            // Overriden ones
+            Self::PackageNotFound(package_address) => f
+                .debug_tuple("PackageNotFound")
+                .field(&package_address.to_string(address_encoder))
+                .finish(),
+            Self::SchemaNotFound(node_id, schema_hash) => f
+                .debug_tuple("SchemaNotFound")
+                .field(&node_id.to_string(address_encoder))
+                .field(schema_hash)
+                .finish(),
+            Self::BlueprintNotFound(package_address, blueprint) => f
+                .debug_tuple("BlueprintNotFound")
+                .field(&package_address.to_string(address_encoder))
+                .field(blueprint)
+                .finish(),
+            Self::ComponentNotFound(component_address) => f
+                .debug_tuple("ComponentNotFound")
+                .field(&component_address.to_string(address_encoder))
+                .finish(),
+            Self::InstanceSchemaNot(component_address, index) => f
+                .debug_tuple("InstanceSchemaNot")
+                .field(&component_address.to_string(address_encoder))
+                .field(index)
+                .finish(),
+            Self::TransactionFailed(runtime_error) => f
+                .debug_tuple("TransactionFailed")
+                .field(&runtime_error.to_string(address_encoder))
+                .finish(),
+            Self::TransactionRejected(rejection_reason) => f
+                .debug_tuple("TransactionRejected")
+                .field(&rejection_reason.to_string(address_encoder))
+                .finish(),
+            // Automatic / Code-gen'd ones
+            Self::NoDefaultAccount => write!(f, "NoDefaultAccount"),
+            Self::NoDefaultPrivateKey => write!(f, "NoDefaultPrivateKey"),
+            Self::NoDefaultOwnerBadge => write!(f, "NoDefaultOwnerBadge"),
+            Self::HomeDirUnknown => write!(f, "HomeDirUnknown"),
+            Self::IOError(err) => f.debug_tuple("IOError").field(err).finish(),
+            Self::IOErrorAtPath(err, path) => f
+                .debug_tuple("IOErrorAtPath")
+                .field(err)
+                .field(path)
+                .finish(),
+            Self::SborDecodeError(err) => f.debug_tuple("SborDecodeError").field(err).finish(),
+            Self::SborEncodeError(err) => f.debug_tuple("SborEncodeError").field(err).finish(),
+            Self::BuildError(err) => f.debug_tuple("BuildError").field(err).finish(),
+            Self::ExtractSchemaError(err) => {
+                f.debug_tuple("ExtractSchemaError").field(err).finish()
             }
-            Error::BlueprintNotFound(package_address, message) => {
-                write!(
-                    f,
-                    "BlueprintNotFound({}, {message})",
-                    package_address.display(&address_encoder)
-                )
+            Self::InvalidPackage(err) => f.debug_tuple("InvalidPackage").field(err).finish(),
+            Self::TransactionConstructionError(err) => f
+                .debug_tuple("TransactionConstructionError")
+                .field(err)
+                .finish(),
+            Self::TransactionValidationError(err) => f
+                .debug_tuple("TransactionValidationError")
+                .field(err)
+                .finish(),
+            Self::TransactionPrepareError(err) => {
+                f.debug_tuple("TransactionPrepareError").field(err).finish()
             }
-            Error::ComponentNotFound(component_address) => {
-                write!(
-                    f,
-                    "ComponentNotFound({})",
-                    component_address.display(&address_encoder)
-                )
+            Self::TransactionAborted(reason) => {
+                f.debug_tuple("TransactionAborted").field(reason).finish()
             }
-            Error::InstanceSchemaNot(component_address, index) => {
-                write!(
-                    f,
-                    "InstanceSchemaNot({}, {index})",
-                    component_address.display(&address_encoder)
-                )
+            Self::LedgerDumpError(err) => f.debug_tuple("LedgerDumpError").field(err).finish(),
+            Self::DecompileError(err) => f.debug_tuple("DecompileError").field(err).finish(),
+            Self::InvalidId(id) => f.debug_tuple("InvalidId").field(id).finish(),
+            Self::InvalidPrivateKey => write!(f, "InvalidPrivateKey"),
+            Self::GotPublicKeyExpectedPrivateKey => write!(f, "GotPublicKeyExpectedPrivateKey"),
+            Self::NonFungibleGlobalIdError(err) => f
+                .debug_tuple("NonFungibleGlobalIdError")
+                .field(err)
+                .finish(),
+            Self::FailedToBuildArguments(err) => {
+                f.debug_tuple("FailedToBuildArguments").field(err).finish()
             }
-            Error::TransactionFailed(runtime_error) => {
-                write!(
-                    f,
-                    "TransactionFailed({})",
-                    runtime_error.display(&address_encoder)
-                )
+            Self::ParseNetworkError(err) => f.debug_tuple("ParseNetworkError").field(err).finish(),
+            Self::OwnerBadgeNotSpecified => write!(f, "OwnerBadgeNotSpecified"),
+            Self::InstructionSchemaValidationError(error) => f
+                .debug_tuple("InstructionSchemaValidationError")
+                .field(error)
+                .finish(),
+            Self::InvalidResourceSpecifier(s) => {
+                f.debug_tuple("InvalidResourceSpecifier").field(s).finish()
             }
-            Error::TransactionRejected(rejection_reason) => {
-                write!(
-                    f,
-                    "TransactionRejected({})",
-                    rejection_reason.display(&address_encoder)
-                )
+            Self::RemoteGenericSubstitutionNotSupported => {
+                write!(f, "RemoteGenericSubstitutionNotSupported")
             }
-            other => write!(f, "{:?}", other),
         }
     }
 }
```
