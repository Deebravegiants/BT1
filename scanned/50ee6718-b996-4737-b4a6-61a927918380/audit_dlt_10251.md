# [?] fix phost crash

## Summary
Severity: Unknown
Chain: Phala
Component: Phala-Network/phala-blockchain
Published: 2021-04-19
Source: https://github.com/Phala-Network/phala-blockchain/commit/f828e2c6f8c515c0a2ee2d42760157d3db0043d4
Type: security-commit

## Details
fix phost crash

## Patch
### scripts/js/yarn.lock
```diff
@@ -2,36 +2,56 @@
 # yarn lockfile v1
 
 
-"@acala-network/api-derive@^0.7.2-11":
-  version "0.7.2-11"
-  resolved "https://registry.yarnpkg.com/@acala-network/api-derive/-/api-derive-0.7.2-11.tgz#30b9580151a0f03a965c95081d116d4db3bc8890"
-  integrity sha512-bb9KI3Zwe0YYvwdPUh8zI3N2FflDlKaJ2u0JoIu1hwjoLj0dt6/cS41xo9jFBwGe5wCHNqcSqjPakhKKbdBxCQ==
+"@acala-network/api-derive@0.7.3":
+  version "0.7.3"
+  resolved "https://registry.yarnpkg.com/@acala-network/api-derive/-/api-derive-0.7.3.tgz#be699a5e35ebd91ad6b450c6766ec090061f4f2b"
+  integrity sha512-ufFgxHaDjOt9x8XmSbFC+uZElqXzi9MGsG+TBhi4crE0wEOjjBWUQ3cEFhVxMftQsX4o+LMnmDr/ixqI2lKKWQ==
   dependencies:
-    "@acala-network/types" "^0.7.2-11"
+    "@acala-network/types" "0.7.3"
     "@babel/runtime" "^7.10.2"
-    "@open-web3/orml-types" "^0.9.1"
+    "@open-web3/orml-types" "^0.9.3"
     "@polkadot/api-derive" "^4.0.3"
 
-"@acala-network/api@^0.7.2-6":
-  version "0.7.2-11"
-  resolved "https://registry.yarnpkg.com/@acala-network/api/-/api-0.7.2-11.tgz#ebdd3ce4555cb2f3f3799c67499e088ff857ecdb"
-  integrity sha512-5I+RWYUWKdsMV2MVY8gzCMXc6cqPFnCbeu5IyMTEaaYV7hiH8AOdJKM+a3my4gUagsYayY3q0+Kfd7YDuYPa4Q==
+"@acala-network/api@^0.7.2-11":
+  version "0.7.3"
+  resolved "https://registry.yarnpkg.com/@acala-network/api/-/api-0.7.3.tgz#df056152f67a83e29a6162444a73252969690157"
+  integrity sha512-fLzJaS05tbz+npE2DibnjoUwQo+2FqStRyWggovw0S8EpLcgQJg2qVxmzrm9FEMcJ5XvrDxeLjIeFcqC4bmTLQ==
   dependencies:
-    "@acala-network/api-derive" "^0.7.2-11"
-    "@acala-network/types" "^0.7.2-11"
+    "@acala-network/api-derive" "0.7.3"
+    "@acala-network/types" "0.7.3"
     "@babel/runtime" "^7.10.2"
     "@open-web3/orml-api-derive" "^0.9.2-0"
     "@polkadot/api" "^4.2.2-4"
     "@polkadot/rpc-core" "^4.2.2-4"
 
+"@acala-network/type-definitions@0.7.3":
+  version "0.7.3"
+  resolved "https://registry.yarnpkg.com/@acala-network/type-definitions/-/type-definitions-0.7.3.tgz#e03872a79a48a39e3055ce5fdf20adc6a9b7ca65"
+  integrity sha512-ZSlBgvUNBhVKCDKFrAoI8EMW3GUfEsmzbTzuXnT/CbI4fiTomiqyZ3LOCP7Mh+N6gkd58xr1nUHRzs8LZ1nsig==
+  dependencies:
+    "@open-web3/orml-type-definitions" "^0.9.3"
+
 "@acala-network/type-definitions@^0.7.2-11":
   version "0.7.2-11"
   resolved "https://registry.yarnpkg.com/@acala-network/type-definitions/-/type-definitions-0.7.2-11.tgz#34ffd9f67ed339726879887f7424bd5ee0fcb45b"
   integrity sha512-1B5Zi0g0C/Ej1LOgr4YUolp385ctnPUI6abDXqDuNHEWTWOonP1TaWxg8CDMrrIaYg6kSjh22FNTrJMdVUm1JA==
   dependencies:
     "@open-web3/orml-type-definitions" "^0.9.1"
 
-"@acala-network/types@^0.7.2-11", "@acala-network/types@^0.7.2-6":
+"@acala-network/types@0.7.3":
+  version "0.7.3"
+  resolved "https://registry.yarnpkg.com/@acala-network/types/-/types-0.7.3.tgz#b288e460af48ca7b155bfc2a55fc03f53ea5f664"
+  integrity sha512-bfy0lZ9Vr8AYxvQf02SaQ2oXqk2NF1zN85DSpbDkT6VDy2OvAfNK3ck9+YZwFBbNbo+Yi83gtmh7VbW5BCMNHA==
+  dependencies:
+    "@acala-network/type-definitions" "0.7.3"
+    "@babel/runtime" "^7.10.2"
+    "@open-web3/api-mobx" "^0.9.3"
+    "@open-web3/orml-types" "^0.9.3"
+    "@polkadot/api" "^4.0.3"
+    "@polkadot/typegen" "^4.0.3"
+    "@polkadot/types" "^4.0.3"
+
+"@acala-network/types@^0.7.2-11":
   version "0.7.2-11"
   resolved "https://registry.yarnpkg.com/@acala-network/types/-/types-0.7.2-11.tgz#f1108b5ff8feabb8ee6674de054c084cf1e79a0c"
   integrity sha512-3bs65pUd7hkau+/dkaO0MyN7qeboRz+HVfZ+Q5jpJSaWB/IVLzXraWtYX/+TMHe5OYWVSXR+W8sJG/CVH+K7Tg==
@@ -262,6 +282,14 @@
     mobx "^5.15.4"
     mobx-utils "^5.5.7"
 
+"@open-web3/api-mobx@^0.9.3":
+  version "0.9.3"
+  resolved "https://registry.yarnpkg.com/@open-web3/api-mobx/-/api-mobx-0.9.3.tgz#bdee9178e36147ce1516eb232c794040898860bc"
+  integrity sha512-bp6rmua/2ddjgPJzpZukxsikiCRyzpEQ/xJl82UhPuXl1QdlvE3N2w4O/MgBzD25NdAvpP2+MAAdFisVfOz02g==
+  dependencies:
+    mobx "^5.15.4"
+    mobx-utils "^5.5.7"
+
 "@open-web3/orml-api-derive@^0.9.2-0":
   version "0.9.2-0"
   resolved "https://registry.yarnpkg.com/@open-web3/orml-api-derive/-/orml-api-derive-0.9.2-0.tgz#deecb21a345a0a38808f7a9f7589d287c5a054e8"
@@ -270,6 +298,11 @@
     memoizee "^0.4.14"
     rxjs "^6.6.6"
 
+"@open-web3/orml-type-definitions@0.9.3", "@open-web3/orml-type-definitions@^0.9.3":
+  version "0.9.3"
+  resolved "https://registry.yarnpkg.com/@open-web3/orml-type-definitions/-/orml-type-definitions-0.9.3.tgz#6bf2ff02c108fa0b4416798f27449f14b16f420f"
+  integrity sha512-Sq88InH7Ca5XbPP2xIzXaZukw0lHG9prpK/y/UA51owscJYQr1y3f6+x8qSUVXMQwowajtODKVVZr4a9wBWi/w==
+
 "@open-web3/orml-type-definitions@^0.9.1":
   version "0.9.1"
   resolved "https://registry.yarnpkg.com/@open-web3/orml-type-definitions/-/orml-type-definitions-0.9.1.tgz#6c0572ec8a879f23a4f45df29abff8af328d1c83"
@@ -282,6 +315,13 @@
   dependencies:
     "@open-web3/orml-type-definitions" "^0.9.1"
 
+"@open-web3/orml-types@^0.9.3":
+  version "0.9.3"
+  resolved "https://registry.yarnpkg.com/@open-web3/orml-types/-/orml-types-0.9.3.tgz#6da0e20cb44e86d7a51202aa8ab82d1742a86a44"
+  integrity sha512-nkIOEL0DfMBsFE5G72cScZnhCf9GsTeGpybPZUmy8rxIjHo1zQNbAD/iLh3V+2qwkR3PJYmxun+Q1GnCIEfF9w==
+  dependencies:
+    "@open-web3/orml-type-definitions" "0.9.3"
+
 "@phala/typedefs@0.0.6":
   version "0.0.6"
   resolved "https://registry.yarnpkg.com/@phala/typedefs/-/typedefs-0.0.6.tgz#99eff6c5e3e5d07cf1cd671e1a0ee9b068742bc9"
@@ -301,7 +341,7 @@
     "@polkadot/x-rxjs" "^6.1.1"
     bn.js "^4.11.9"
 
-"@polkadot/api@4.5.1", "@polkadot/api@^4.0.3", "@polkadot/api@^4.2.2-4", "@polkadot/api@^4.4.1":
+"@polkadot/api@4.5.1", "@polkadot/api@^4.0.3", "@polkadot/api@^4.2.2-4", "@polkadot/api@^4.5.1":
   version "4.5.1"
   resolved "https://registry.yarnpkg.com/@polkadot/api/-/api-4.5.1.tgz#02672ebb4c34110048fd4308974c20f03328be0f"
   integrity sha512-b9CBG1ZGhyFwXDiVP0vKZbY8RdW2rbtHxw3BYPYUZ4bk6NVsDCk7vPD2z3B19RxHOv7Chkjtx+b5MU6ASfKRhg==
@@ -416,7 +456,7 @@
     "@types/bn.js" "^4.11.6"
     bn.js "^4.11.9"
 
-"@polkadot/util-crypto@6.1.1", "@polkadot/util-crypto@^6.0.5", "@polkadot/util-crypto@^6.1.1":
+"@polkadot/util-crypto@6.1.1", "@polkadot/util-crypto@^6.1.1":
   version "6.1.1"
   resolved "https://registry.yarnpkg.com/@polkadot/util-crypto/-/util-crypto-6.1.1.tgz#dc9ee86656bbaf59b41c5a1cf40fa025b44aaf27"
   integrity sha512-xKDqudvMCirQZ4df2PiWEdlNntNn5gUx/2gTNId7MoE4j4y0edLTwiQ6B2EgRCyLxCaIY+sw6Z5NL5ik1NHdcw==
```

### standalone/phost/src/main.rs
```diff
@@ -365,7 +365,9 @@ async fn batch_sync_block(
             .iter()
             .map(|b| HeaderToSync {
                 header: b.block.block.header.clone(),
-                justification: b.block.justifications.clone().unwrap().into_justification(GRANDPA_ENGINE_ID),
+                justification: b.block.justifications.clone().map(|v|
+                    v.into_justification(GRANDPA_ENGINE_ID)
+                ).flatten(),
             })
             .collect();
 
```
