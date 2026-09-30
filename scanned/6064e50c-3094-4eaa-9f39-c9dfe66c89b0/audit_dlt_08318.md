# [?] fix redos vulnerability (#2412)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2023-03-01
Source: https://github.com/otter-sec/anchor/commit/90383a7a221ab7108d99a3a995805f3620cd4cd5
Type: security-commit

## Details
fix redos vulnerability (#2412)

## Patch
### docs/programs/tic-tac-toe/package.json
```diff
@@ -3,11 +3,11 @@
         "@project-serum/anchor": "0.24.1"
     },
     "devDependencies": {
-        "@types/mocha": "^9.0.0",
         "@types/chai": "^4.3.0",
+        "@types/mocha": "^9.0.0",
         "chai": "^4.3.4",
         "chai-as-promised": "^7.1.1",
-        "mocha": "^9.0.3",
+        "mocha": "9.2.2",
         "ts-mocha": "^8.0.0",
         "typescript": "^4.3.5"
     }
```

### docs/programs/tic-tac-toe/yarn.lock
```diff
@@ -357,10 +357,10 @@ check-error@^1.0.2:
   resolved "https://registry.yarnpkg.com/check-error/-/check-error-1.0.2.tgz#574d312edd88bb5dd8912e9286dd6c0aed4aac82"
   integrity sha1-V00xLt2Iu13YkS6Sht1sCu1KrII=
 
-chokidar@3.5.2:
-  version "3.5.2"
-  resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.2.tgz#dba3976fcadb016f66fd365021d91600d01c1e75"
-  integrity sha512-ekGhOnNVPgT77r4K/U3GDhu+FQ2S8TnK/s2KbIGXi0SZWuwkZ2QNyfWdZW+TVfn84DpEP7rLeCt2UI6bJ8GwbQ==
+chokidar@3.5.3:
+  version "3.5.3"
+  resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.3.tgz#1cf37c8707b932bd1af1ae22c0432e2acd1903bd"
+  integrity sha512-Dr3sfKRP6oTcjf2JmUmFJfeVMvXBdegxB0iVQ5eb2V10uFJUCAS8OByZdVAyVb8xXNz3GjjTgj9kLWsZTqE6kw==
   dependencies:
     anymatch "~3.1.2"
     braces "~3.0.2"
@@ -420,10 +420,10 @@ crypto-hash@^1.3.0:
   resolved "https://registry.yarnpkg.com/crypto-hash/-/crypto-hash-1.3.0.tgz#b402cb08f4529e9f4f09346c3e275942f845e247"
   integrity sha512-lyAZ0EMyjDkVvz8WOeVnuCPvKVBXcMv1l5SVqO1yC7PzTwrD/pPje/BIRbWhMoPe436U+Y2nD7f5bFx0kt+Sbg==
 
-debug@4.3.2:
-  version "4.3.2"
-  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.2.tgz#f0a49c18ac8779e31d4a0c6029dfb76873c7428b"
-  integrity sha512-mOp8wKcvj7XxC78zLgw/ZA+6TSgkoE2C/ienthhRD298T7UNwAg9diBpLRxC0mOezLl4B0xV7M0cCO6P/O0Xhw==
+debug@4.3.3:
+  version "4.3.3"
+  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.3.tgz#04266e0b70a98d4462e6e288e38259213332b664"
+  integrity sha512-/zxw5+vh1Tfv+4Qn7a5nsbcJKPaSvCDhojn6FEl9vupwK2VCSDtEiEtqr8DFtzYFOdz63LBkxec7DYuc2jon6Q==
   dependencies:
     ms "2.1.2"
 
@@ -559,10 +559,10 @@ glob-parent@~5.1.2:
   dependencies:
     is-glob "^4.0.1"
 
-glob@7.1.7:
-  version "7.1.7"
-  resolved "https://registry.yarnpkg.com/glob/-/glob-7.1.7.tgz#3b193e9233f01d42d0b3f78294bbeeb418f94a90"
-  integrity sha512-OvD9ENzPLbegENnYP5UUfJIirTg4+XwMWGaQfQTY0JenxNvvIKP3U3/tAQSPIu/lHxXYSZmpXlUHeqAIdKzBLQ==
+glob@7.2.0:
+  version "7.2.0"
+  resolved "https://registry.yarnpkg.com/glob/-/glob-7.2.0.tgz#d15535af7732e02e948f4c41628bd910293f6023"
+  integrity sha512-lmLf6gtyrPq8tTjSmrO94wBeQbFR3HbLHbuyD69wuyQkImp2hWqMGB47OX65FBkPffO641IP9jWa1z4ivqG26Q==
   dependencies:
     fs.realpath "^1.0.0"
     inflight "^1.0.4"
@@ -767,7 +767,14 @@ minimalistic-crypto-utils@^1.0.1:
   resolved "https://registry.yarnpkg.com/minimalistic-crypto-utils/-/minimalistic-crypto-utils-1.0.1.tgz#f6c00c1c0b082246e5c4d99dfb8c7c083b2b582a"
   integrity sha1-9sAMHAsIIkblxNmd+4x8CDsrWCo=
 
-minimatch@3.0.4, minimatch@^3.0.4:
+minimatch@4.2.1:
+  version "4.2.1"
+  resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-4.2.1.tgz#40d9d511a46bdc4e563c22c3080cde9c0d8299b4"
+  integrity sha512-9Uq1ChtSZO+Mxa/CL1eGizn2vRn3MlLgzhT0Iz8zaY8NdvxvB0d5QdPFmCKf7JKA9Lerx5vRrnwO03jsSfGG9g==
+  dependencies:
+    brace-expansion "^1.1.7"
+
+minimatch@^3.0.4:
   version "3.0.4"
   resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-3.0.4.tgz#5166e286457f03306064be5497e8dbb0c3d32083"
   integrity sha512-yJHVQEhyqPLUTgt9B83PXu6W3rx4MvvHvSUvToogpwoGDOUQ+yDrR0HRot+yOCdCO7u4hX3pWft6kWBBcqh0UA==
@@ -786,32 +793,32 @@ mkdirp@^0.5.1:
   dependencies:
     minimist "^1.2.5"
 
-mocha@^9.0.3:
-  version "9.1.3"
-  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.1.3.tgz#8a623be6b323810493d8c8f6f7667440fa469fdb"
-  integrity sha512-Xcpl9FqXOAYqI3j79pEtHBBnQgVXIhpULjGQa7DVb0Po+VzmSIK9kanAiWLHoRR/dbZ2qpdPshuXr8l1VaHCzw==
+mocha@9.2.2:
+  version "9.2.2"
+  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.2.2.tgz#d70db46bdb93ca57402c809333e5a84977a88fb9"
+  integrity sha512-L6XC3EdwT6YrIk0yXpavvLkn8h+EU+Y5UcCHKECyMbdUIxyMuZj4bX4U9e1nvnvUUvQVsV2VHQr5zLdcUkhW/g==
   dependencies:
     "@ungap/promise-all-settled" "1.1.2"
     ansi-colors "4.1.1"
     browser-stdout "1.3.1"
-    chokidar "3.5.2"
-    debug "4.3.2"
+    chokidar "3.5.3"
+    debug "4.3.3"
     diff "5.0.0"
     escape-string-regexp "4.0.0"
     find-up "5.0.0"
-    glob "7.1.7"
+    glob "7.2.0"
     growl "1.10.5"
     he "1.2.0"
     js-yaml "4.1.0"
     log-symbols "4.1.0"
-    minimatch "3.0.4"
+    minimatch "4.2.1"
     ms "2.1.3"
-    nanoid "3.1.25"
+    nanoid "3.3.1"
     serialize-javascript "6.0.0"
     strip-json-comments "3.1.1"
     supports-color "8.1.1"
     which "2.0.2"
-    workerpool "6.1.5"
+    workerpool "6.2.0"
     yargs "16.2.0"
     yargs-parser "20.2.4"
     yargs-unparser "2.0.0"
@@ -826,10 +833,10 @@ ms@2.1.3:
   resolved "https://registry.yarnpkg.com/ms/-/ms-2.1.3.tgz#574c8138ce1d2b5861f0b44579dbadd60c6615b2"
   integrity sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==
 
-nanoid@3.1.25:
-  version "3.1.25"
-  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.1.25.tgz#09ca32747c0e543f0e1814b7d3793477f9c8e152"
-  integrity sha512-rdwtIXaXCLFAQbnfqDRnI6jaRHp9fTcYBjtFKE8eezcZ7LuLjhUaQGNeMXf1HmRoCH32CLz6XwX0TtxEOS/A3Q==
+nanoid@3.3.1:
+  version "3.3.1"
+  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.3.1.tgz#6347a18cac88af88f58af0b3594b723d5e99bb35"
+  integrity sha512-n6Vs/3KGyxPQd6uO0eH4Bv0ojGSUvuLlIHtC3Y0kEO23YRge8H9x1GCzLn28YX0H66pMkxuaeESFq4tKISKwdw==
 
 no-case@^3.0.4:
   version "3.0.4"
@@ -1144,10 +1151,10 @@ which@2.0.2:
   dependencies:
     isexe "^2.0.0"
 
-workerpool@6.1.5:
-  version "6.1.5"
-  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.1.5.tgz#0f7cf076b6215fd7e1da903ff6f22ddd1886b581"
-  integrity sha512-XdKkCK0Zqc6w3iTxLckiuJ81tiD/o5rBE/m+nXpRCB+/Sq4DqkfXZ/x0jW02DG1tGsfUGXbTJyZDP+eu67haSw==
+workerpool@6.2.0:
+  version "6.2.0"
+  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.2.0.tgz#827d93c9ba23ee2019c3ffaff5c27fccea289e8b"
+  integrity sha512-Rsk5qQHJ9eowMH28Jwhe8HEbmdYDX4lwoMWshiCXugjtHqMD9ZbiqSDLxcsfdqsETPzVUtX5s1Z5kStiIM6l4A==
 
 wrap-ansi@^7.0.0:
   version "7.0.0"
```

### examples/tutorial/package.json
```diff
@@ -16,7 +16,7 @@
     "@coral-xyz/anchor": "file:../../ts/packages/anchor"
   },
   "devDependencies": {
-    "mocha": "^9.1.3",
+    "mocha": "9.2.2",
     "prettier": "^2.5.1"
   }
 }
```

### examples/tutorial/yarn.lock
```diff
@@ -305,10 +305,10 @@ chalk@^4.1.0:
     ansi-styles "^4.1.0"
     supports-color "^7.1.0"
 
-chokidar@3.5.2:
-  version "3.5.2"
-  resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.2.tgz#dba3976fcadb016f66fd365021d91600d01c1e75"
-  integrity sha512-ekGhOnNVPgT77r4K/U3GDhu+FQ2S8TnK/s2KbIGXi0SZWuwkZ2QNyfWdZW+TVfn84DpEP7rLeCt2UI6bJ8GwbQ==
+chokidar@3.5.3:
+  version "3.5.3"
+  resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.3.tgz#1cf37c8707b932bd1af1ae22c0432e2acd1903bd"
+  integrity sha512-Dr3sfKRP6oTcjf2JmUmFJfeVMvXBdegxB0iVQ5eb2V10uFJUCAS8OByZdVAyVb8xXNz3GjjTgj9kLWsZTqE6kw==
   dependencies:
     anymatch "~3.1.2"
     braces "~3.0.2"
@@ -363,10 +363,10 @@ crypto-hash@^1.3.0:
   resolved "https://registry.yarnpkg.com/crypto-hash/-/crypto-hash-1.3.0.tgz#b402cb08f4529e9f4f09346c3e275942f845e247"
   integrity sha512-lyAZ0EMyjDkVvz8WOeVnuCPvKVBXcMv1l5SVqO1yC7PzTwrD/pPje/BIRbWhMoPe436U+Y2nD7f5bFx0kt+Sbg==
 
-debug@4.3.2:
-  version "4.3.2"
-  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.2.tgz#f0a49c18ac8779e31d4a0c6029dfb76873c7428b"
-  integrity sha512-mOp8wKcvj7XxC78zLgw/ZA+6TSgkoE2C/ienthhRD298T7UNwAg9diBpLRxC0mOezLl4B0xV7M0cCO6P/O0Xhw==
+debug@4.3.3:
+  version "4.3.3"
+  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.3.tgz#04266e0b70a98d4462e6e288e38259213332b664"
+  integrity sha512-/zxw5+vh1Tfv+4Qn7a5nsbcJKPaSvCDhojn6FEl9vupwK2VCSDtEiEtqr8DFtzYFOdz63LBkxec7DYuc2jon6Q==
   dependencies:
     ms "2.1.2"
 
@@ -482,10 +482,10 @@ glob-parent@~5.1.2:
   dependencies:
     is-glob "^4.0.1"
 
-glob@7.1.7:
-  version "7.1.7"
-  resolved "https://registry.yarnpkg.com/glob/-/glob-7.1.7.tgz#3b193e9233f01d42d0b3f78294bbeeb418f94a90"
-  integrity sha512-OvD9ENzPLbegENnYP5UUfJIirTg4+XwMWGaQfQTY0JenxNvvIKP3U3/tAQSPIu/lHxXYSZmpXlUHeqAIdKzBLQ==
+glob@7.2.0:
+  version "7.2.0"
+  resolved "https://registry.yarnpkg.com/glob/-/glob-7.2.0.tgz#d15535af7732e02e948f4c41628bd910293f6023"
+  integrity sha512-lmLf6gtyrPq8tTjSmrO94wBeQbFR3HbLHbuyD69wuyQkImp2hWqMGB47OX65FBkPffO641IP9jWa1z4ivqG26Q==
   dependencies:
     fs.realpath "^1.0.0"
     inflight "^1.0.4"
@@ -646,39 +646,46 @@ lower-case@^2.0.2:
   dependencies:
     tslib "^2.0.3"
 
-minimatch@3.0.4, minimatch@^3.0.4:
+minimatch@4.2.1:
+  version "4.2.1"
+  resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-4.2.1.tgz#40d9d511a46bdc4e563c22c3080cde9c0d8299b4"
+  integrity sha512-9Uq1ChtSZO+Mxa/CL1eGizn2vRn3MlLgzhT0Iz8zaY8NdvxvB0d5QdPFmCKf7JKA9Lerx5vRrnwO03jsSfGG9g==
+  dependencies:
+    brace-expansion "^1.1.7"
+
+minimatch@^3.0.4:
   version "3.0.4"
   resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-3.0.4.tgz#5166e286457f03306064be5497e8dbb0c3d32083"
   integrity sha512-yJHVQEhyqPLUTgt9B83PXu6W3rx4MvvHvSUvToogpwoGDOUQ+yDrR0HRot+yOCdCO7u4hX3pWft6kWBBcqh0UA==
   dependencies:
     brace-expansion "^1.1.7"
 
-mocha@^9.1.3:
-  version "9.1.3"
-  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.1.3.tgz#8a623be6b323810493d8c8f6f7667440fa469fdb"
-  integrity sha512-Xcpl9FqXOAYqI3j79pEtHBBnQgVXIhpULjGQa7DVb0Po+VzmSIK9kanAiWLHoRR/dbZ2qpdPshuXr8l1VaHCzw==
+mocha@9.2.2:
+  version "9.2.2"
+  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.2.2.tgz#d70db46bdb93ca57402c809333e5a84977a88fb9"
+  integrity sha512-L6XC3EdwT6YrIk0yXpavvLkn8h+EU+Y5UcCHKECyMbdUIxyMuZj4bX4U9e1nvnvUUvQVsV2VHQr5zLdcUkhW/g==
   dependencies:
     "@ungap/promise-all-settled" "1.1.2"
     ansi-colors "4.1.1"
     browser-stdout "1.3.1"
-    chokidar "3.5.2"
-    debug "4.3.2"
+    chokidar "3.5.3"
+    debug "4.3.3"
     diff "5.0.0"
     escape-string-regexp "4.0.0"
     find-up "5.0.0"
-    glob "7.1.7"
+    glob "7.2.0"
     growl "1.10.5"
     he "1.2.0"
     js-yaml "4.1.0"
     log-symbols "4.1.0"
-    minimatch "3.0.4"
+    minimatch "4.2.1"
     ms "2.1.3"
-    nanoid "3.1.25"
+    nanoid "3.3.1"
     serialize-javascript "6.0.0"
     strip-json-comments "3.1.1"
     supports-color "8.1.1"
     which "2.0.2"
-    workerpool "6.1.5"
+    workerpool "6.2.0"
     yargs "16.2.0"
     yargs-parser "20.2.4"
     yargs-unparser "2.0.0"
@@ -693,10 +700,10 @@ ms@2.1.3:
   resolved "https://registry.yarnpkg.com/ms/-/ms-2.1.3.tgz#574c8138ce1d2b5861f0b44579dbadd60c6615b2"
   integrity sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==
 
-nanoid@3.1.25:
-  version "3.1.25"
-  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.1.25.tgz#09ca32747c0e543f0e1814b7d3793477f9c8e152"
-  integrity sha512-rdwtIXaXCLFAQbnfqDRnI6jaRHp9fTcYBjtFKE8eezcZ7LuLjhUaQGNeMXf1HmRoCH32CLz6XwX0TtxEOS/A3Q==
+nanoid@3.3.1:
+  version "3.3.1"
+  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.3.1.tgz#6347a18cac88af88f58af0b3594b723d5e99bb35"
+  integrity sha512-n6Vs/3KGyxPQd6uO0eH4Bv0ojGSUvuLlIHtC3Y0kEO23YRge8H9x1GCzLn28YX0H66pMkxuaeESFq4tKISKwdw==
 
 no-case@^3.0.4:
   version "3.0.4"
@@ -945,10 +952,10 @@ which@2.0.2:
   dependencies:
     isexe "^2.0.0"
 
-workerpool@6.1.5:
-  version "6.1.5"
-  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.1.5.tgz#0f7cf076b6215fd7e1da903ff6f22ddd1886b581"
-  integrity sha512-XdKkCK0Zqc6w3iTxLckiuJ81tiD/o5rBE/m+nXpRCB+/Sq4DqkfXZ/x0jW02DG1tGsfUGXbTJyZDP+eu67haSw==
+workerpool@6.2.0:
+  version "6.2.0"
+  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.2.0.tgz#827d93c9ba23ee2019c3ffaff5c27fccea289e8b"
+  integrity sha512-Rsk5qQHJ9eowMH28Jwhe8HEbmdYDX4lwoMWshiCXugjtHqMD9ZbiqSDLxcsfdqsETPzVUtX5s1Z5kStiIM6l4A==
 
 wrap-ansi@^7.0.0:
   version "7.0.0"
```

### tests/anchor-cli-idl/package.json
```diff
@@ -17,6 +17,6 @@
     "test": "./test.sh"
   },
   "dependencies": {
-    "mocha": "^9.1.3"
+    "mocha": "9.2.2"
   }
 }
```

### tests/misc/package.json
```diff
@@ -17,6 +17,6 @@
     "test": "anchor test"
   },
   "dependencies": {
-    "mocha": "^9.1.3"
+    "mocha": "9.2.2"
   }
 }
```

### tests/package.json
```diff
@@ -44,23 +44,23 @@
   ],
   "dependencies": {
     "@coral-xyz/anchor": "file:../ts/packages/anchor",
-    "@project-serum/common": "^0.0.1-beta.3",
-    "@project-serum/serum": "^0.13.60",
     "@coral-xyz/spl-associated-token-account": "file:../ts/packages/spl-associated-token-account",
     "@coral-xyz/spl-token": "file:../ts/packages/spl-token",
+    "@project-serum/common": "^0.0.1-beta.3",
+    "@project-serum/serum": "^0.13.60",
     "@solana/spl-token": "^0.1.8",
     "@solana/web3.js": "^1.68.0"
   },
   "resolutions": {
     "@coral-xyz/anchor/@solana/web3.js": "^1.68.0"
   },
   "devDependencies": {
+    "@types/bn.js": "^5.1.1",
     "@types/chai": "^4.3.0",
     "@types/mocha": "^9.1.0",
     "@types/node": "^14.14.37",
-    "@types/bn.js": "^5.1.1",
     "chai": "^4.3.4",
-    "mocha": "^10.0.0",
+    "mocha": "9.2.2",
     "prettier": "^2.5.1",
     "ts-mocha": "^10.0.0",
     "tsc": "^2.0.4",
```

### tests/yarn.lock
```diff
@@ -303,9 +303,9 @@ ansi-styles@^4.0.0, ansi-styles@^4.1.0:
     color-convert "^2.0.1"
 
 anymatch@~3.1.2:
-  version "3.1.2"
-  resolved "https://registry.yarnpkg.com/anymatch/-/anymatch-3.1.2.tgz#c0557c096af32f106198f4f4e2a383537e378716"
-  integrity sha512-P43ePfOAIupkguHUycrc4qJ9kz8ZiuOUijaETwX7THt0Y/GNK7v0aa8rY816xWjZ7rJdA5XdMcpVFTKMq+RvWg==
+  version "3.1.3"
+  resolved "https://registry.yarnpkg.com/anymatch/-/anymatch-3.1.3.tgz#790c58b19ba1720a84205b57c618d5ad8524973e"
+  integrity sha512-KMReFUr0B4t+D+OBkjR3KYqvocp2XaSzO55UcB6mgQMd3KbcE+mWTyvVV7D/zsdEbNnV6acZUutkiHQXvTr1Rw==
   dependencies:
     normalize-path "^3.0.0"
     picomatch "^2.0.4"
@@ -457,12 +457,7 @@ camelcase@^5.3.1:
   resolved "https://registry.yarnpkg.com/camelcase/-/camelcase-5.3.1.tgz#e3c9b31569e106811df242f715725a1f4c494320"
   integrity sha512-L28STB170nwWS63UjtlEOE3dldQApaJXZkOI1uMFfzf3rRuPegHaHesyee+YxQ+W6SvRDQV6UrdOdRiR153wJg==
 
-camelcase@^6.0.0:
-  version "6.2.0"
-  resolved "https://registry.yarnpkg.com/camelcase/-/camelcase-6.2.0.tgz#924af881c9d525ac9d87f40d964e5cea982a1809"
-  integrity sha512-c7wVvbw3f37nuobQNtgsgG9POC9qMbNuMQmTCqZv23b6MIz0fcYpBiOlv9gEN/hdLdnZTDQhg6e9Dq5M1vKvfg==
-
-camelcase@^6.3.0:
+camelcase@^6.0.0, camelcase@^6.3.0:
   version "6.3.0"
   resolved "https://registry.yarnpkg.com/camelcase/-/camelcase-6.3.0.tgz#5685b95eb209ac9c0c177467778c9c84df58ba9a"
   integrity sha512-Gmy6FhYlCY7uOElZUSbxo2UCDH8owEk996gkbrpsgGtrJLM3J7jGxl9Ic7Qwwj4ivOE5AWZWRMecDdF7hqGjFA==
@@ -492,21 +487,6 @@ check-error@^1.0.2:
   resolved "https://registry.yarnpkg.com/check-error/-/check-error-1.0.2.tgz#574d312edd88bb5dd8912e9286dd6c0aed4aac82"
   integrity sha1-V00xLt2Iu13YkS6Sht1sCu1KrII=
 
-chokidar@3.5.2:
-  version "3.5.2"
-  resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.2.tgz#dba3976fcadb016f66fd365021d91600d01c1e75"
-  integrity sha512-ekGhOnNVPgT77r4K/U3GDhu+FQ2S8TnK/s2KbIGXi0SZWuwkZ2QNyfWdZW+TVfn84DpEP7rLeCt2UI6bJ8GwbQ==
-  dependencies:
-    anymatch "~3.1.2"
-    braces "~3.0.2"
-    glob-parent "~5.1.2"
-    is-binary-path "~2.1.0"
-    is-glob "~4.0.1"
-    normalize-path "~3.0.0"
-    readdirp "~3.6.0"
-  optionalDependencies:
-    fsevents "~2.3.2"
-
 chokidar@3.5.3:
   version "3.5.3"
   resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.3.tgz#1cf37c8707b932bd1af1ae22c0432e2acd1903bd"
@@ -551,7 +531,7 @@ commander@^2.20.3:
 concat-map@0.0.1:
   version "0.0.1"
   resolved "https://registry.yarnpkg.com/concat-map/-/concat-map-0.0.1.tgz#d8a96bd77fd68df7793a73036a3ba0d5405d477b"
-  integrity sha1-2Klr13/Wjfd5OnMDajug1UBdR3s=
+  integrity sha512-/Srv4dswyQNBfohGpz9o6Yb3Gz3SrUDqBH5rTuhGR7ahtlbYKnVxw2bCFMRljaA7EXHaXZ8wsHdodFvbkhKmqg==
 
 cross-fetch@^3.1.5:
   version "3.1.5"
@@ -565,10 +545,10 @@ crypto-hash@^1.3.0:
   resolved "https://registry.yarnpkg.com/crypto-hash/-/crypto-hash-1.3.0.tgz#b402cb08f4529e9f4f09346c3e275942f845e247"
   integrity sha512-lyAZ0EMyjDkVvz8WOeVnuCPvKVBXcMv1l5SVqO1yC7PzTwrD/pPje/BIRbWhMoPe436U+Y2nD7f5bFx0kt+Sbg==
 
-debug@4.3.2:
-  version "4.3.2"
-  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.2.tgz#f0a49c18ac8779e31d4a0c6029dfb76873c7428b"
-  integrity sha512-mOp8wKcvj7XxC78zLgw/ZA+6TSgkoE2C/ienthhRD298T7UNwAg9diBpLRxC0mOezLl4B0xV7M0cCO6P/O0Xhw==
+debug@4.3.3:
+  version "4.3.3"
+  resolved "https://registry.yarnpkg.com/debug/-/debug-4.3.3.tgz#04266e0b70a98d4462e6e288e38259213332b664"
+  integrity sha512-/zxw5+vh1Tfv+4Qn7a5nsbcJKPaSvCDhojn6FEl9vupwK2VCSDtEiEtqr8DFtzYFOdz63LBkxec7DYuc2jon6Q==
   dependencies:
     ms "2.1.2"
 
@@ -696,7 +676,7 @@ flat@^5.0.2:
 fs.realpath@^1.0.0:
   version "1.0.0"
   resolved "https://registry.yarnpkg.com/fs.realpath/-/fs.realpath-1.0.0.tgz#1504ad2523158caa40db4a2787cb01411994ea4f"
-  integrity sha1-FQStJSMVjKpA20onh8sBQRmU6k8=
+  integrity sha512-OO0pH2lK6a0hZnAdau5ItzHPI6pUlvI7jMVnxUQRtw4owF2wk8lOSabtGDCTP4Ggrg2MbGnWO9X8K1t4+fGMDw==
 
 fsevents@~2.3.2:
   version "2.3.2"
@@ -720,18 +700,6 @@ glob-parent@~5.1.2:
   dependencies:
     is-glob "^4.0.1"
 
-glob@7.1.7:
-  version "7.1.7"
-  resolved "https://registry.yarnpkg.com/glob/-/glob-7.1.7.tgz#3b193e9233f01d42d0b3f78294bbeeb418f94a90"
-  integrity sha512-OvD9ENzPLbegENnYP5UUfJIirTg4+XwMWGaQfQTY0JenxNvvIKP3U3/tAQSPIu/lHxXYSZmpXlUHeqAIdKzBLQ==
-  dependencies:
-    fs.realpath "^1.0.0"
-    inflight "^1.0.4"
-    inherits "2"
-    minimatch "^3.0.4"
-    once "^1.3.0"
-    path-is-absolute "^1.0.0"
-
 glob@7.2.0:
   version "7.2.0"
   resolved "https://registry.yarnpkg.com/glob/-/glob-7.2.0.tgz#d15535af7732e02e948f4c41628bd910293f6023"
@@ -767,7 +735,7 @@ ieee754@^1.2.1:
 inflight@^1.0.4:
   version "1.0.6"
   resolved "https://registry.yarnpkg.com/inflight/-/inflight-1.0.6.tgz#49bd6331d7d02d0c09bc910a1075ba8165b56df9"
-  integrity sha1-Sb1jMdfQLQwJvJEKEHW6gWW1bfk=
+  integrity sha512-k92I/b08q4wvFscXCLvqfsHCrjrF7yiXsQuIVvVE7N82W3+aqpzuUdBbfhWcy/FZR3/4IgflMgKLOsvPDrGCJA==
   dependencies:
     once "^1.3.0"
     wrappy "1"
@@ -787,7 +755,7 @@ is-binary-path@~2.1.0:
 is-extglob@^2.1.1:
   version "2.1.1"
   resolved "https://registry.yarnpkg.com/is-extglob/-/is-extglob-2.1.1.tgz#a88c02535791f02ed37c76a1b9ea9773c833f8c2"
-  integrity sha1-qIwCU1eR8C7TfHahueqXc8gz+MI=
+  integrity sha512-SbKbANkN603Vi4jEZv49LeVJMn4yGwsbzZworEoyEiutsN3nJYdbO36zfhGJ6QEDpOZIFkDtnq5JRxmvl3jsoQ==
 
 is-fullwidth-code-point@^3.0.0:
   version "3.0.0"
@@ -819,7 +787,7 @@ is-unicode-supported@^0.1.0:
 isexe@^2.0.0:
   version "2.0.0"
   resolved "https://registry.yarnpkg.com/isexe/-/isexe-2.0.0.tgz#e8fbf374dc556ff8947a10dcb0572d633f2cfa10"
-  integrity sha1-6PvzdNxVb/iUehDcsFctYz8s+hA=
+  integrity sha512-RHxMLp9lnKHGHRng9QFhRCMbYAcVpn69smSGcq3f36xjgVVWThj4qqLbTLlq7Ssj8B+fIQ1EuCEGI2lKsyQeIw==
 
 isomorphic-ws@^4.0.1:
   version "4.0.1"
@@ -913,10 +881,10 @@ make-error@^1.1.1:
   resolved "https://registry.yarnpkg.com/make-error/-/make-error-1.3.6.tgz#2eb2e37ea9b67c4891f684a1394799af484cf7a2"
   integrity sha512-s8UhlNe7vPKomQhC1qFelMokr/Sc3AgNbso3n74mVPA5LTZwkB9NlXf4XPamLxJE8h0gh73rM94xvwRT2CVInw==
 
-minimatch@3.0.4, minimatch@^3.0.4:
-  version "3.0.4"
-  resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-3.0.4.tgz#5166e286457f03306064be5497e8dbb0c3d32083"
-  integrity sha512-yJHVQEhyqPLUTgt9B83PXu6W3rx4MvvHvSUvToogpwoGDOUQ+yDrR0HRot+yOCdCO7u4hX3pWft6kWBBcqh0UA==
+minimatch@4.2.1:
+  version "4.2.1"
+  resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-4.2.1.tgz#40d9d511a46bdc4e563c22c3080cde9c0d8299b4"
+  integrity sha512-9Uq1ChtSZO+Mxa/CL1eGizn2vRn3MlLgzhT0Iz8zaY8NdvxvB0d5QdPFmCKf7JKA9Lerx5vRrnwO03jsSfGG9g==
   dependencies:
     brace-expansion "^1.1.7"
 
@@ -927,6 +895,13 @@ minimatch@5.0.1:
   dependencies:
     brace-expansion "^2.0.1"
 
+minimatch@^3.0.4:
+  version "3.1.2"
+  resolved "https://registry.yarnpkg.com/minimatch/-/minimatch-3.1.2.tgz#19cd194bfd3e428f049a70817c038d89ab4be35b"
+  integrity sha512-J7p63hRiAjw1NDEww1W7i37+ByIrOWO5XQQAzZ3VOcL0PNybwpfmV/N05zFAzwQ9USyEcX6t3UO+K5aqBQOIHw==
+  dependencies:
+    brace-expansion "^1.1.7"
+
 minimist@^1.2.0, minimist@^1.2.5:
   version "1.2.6"
   resolved "https://registry.yarnpkg.com/minimist/-/minimist-1.2.6.tgz#8637a5b759ea0d6e98702cfb3a9283323c93af44"
@@ -939,60 +914,59 @@ mkdirp@^0.5.1:
   dependencies:
     minimist "^1.2.5"
 
-mocha@^10.0.0:
-  version "10.0.0"
-  resolved "https://registry.yarnpkg.com/mocha/-/mocha-10.0.0.tgz#205447d8993ec755335c4b13deba3d3a13c4def9"
-  integrity sha512-0Wl+elVUD43Y0BqPZBzZt8Tnkw9CMUdNYnUsTfOM1vuhJVZL+kiesFYsqwBkEEuEixaiPe5ZQdqDgX2jddhmoA==
+mocha@9.2.2:
+  version "9.2.2"
+  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.2.2.tgz#d70db46bdb93ca57402c809333e5a84977a88fb9"
+  integrity sha512-L6XC3EdwT6YrIk0yXpavvLkn8h+EU+Y5UcCHKECyMbdUIxyMuZj4bX4U9e1nvnvUUvQVsV2VHQr5zLdcUkhW/g==
   dependencies:
     "@ungap/promise-all-settled" "1.1.2"
     ansi-colors "4.1.1"
     browser-stdout "1.3.1"
     chokidar "3.5.3"
-    debug "4.3.4"
+    debug "4.3.3"
     diff "5.0.0"
     escape-string-regexp "4.0.0"
     find-up "5.0.0"
     glob "7.2.0"
+    growl "1.10.5"
     he "1.2.0"
     js-yaml "4.1.0"
     log-symbols "4.1.0"
-    minimatch "5.0.1"
+    minimatch "4.2.1"
     ms "2.1.3"
-    nanoid "3.3.3"
+    nanoid "3.3.1"
     serialize-javascript "6.0.0"
     strip-json-comments "3.1.1"
     supports-color "8.1.1"
-    workerpool "6.2.1"
+    which "2.0.2"
+    workerpool "6.2.0"
     yargs "16.2.0"
     yargs-parser "20.2.4"
     yargs-unparser "2.0.0"
 
-mocha@^9.1.3:
-  version "9.1.3"
-  resolved "https://registry.yarnpkg.com/mocha/-/mocha-9.1.3.tgz#8a623be6b323810493d8c8f6f7667440fa469fdb"
-  integrity sha512-Xcpl9FqXOAYqI3j79pEtHBBnQgVXIhpULjGQa7DVb0Po+VzmSIK9kanAiWLHoRR/dbZ2qpdPshuXr8l1VaHCzw==
+mocha@^10.0.0:
+  version "10.2.0"
+  resolved "https://registry.yarnpkg.com/mocha/-/mocha-10.2.0.tgz#1fd4a7c32ba5ac372e03a17eef435bd00e5c68b8"
+  integrity sha512-IDY7fl/BecMwFHzoqF2sg/SHHANeBoMMXFlS9r0OXKDssYE1M5O43wUY/9BVPeIvfH2zmEbBfseqN9gBQZzXkg==
   dependencies:
-    "@ungap/promise-all-settled" "1.1.2"
     ansi-colors "4.1.1"
     browser-stdout "1.3.1"
-    chokidar "3.5.2"
-    debug "4.3.2"
+    chokidar "3.5.3"
+    debug "4.3.4"
     diff "5.0.0"
     escape-string-regexp "4.0.0"
     find-up "5.0.0"
-    glob "7.1.7"
-    growl "1.10.5"
+    glob "7.2.0"
     he "1.2.0"
     js-yaml "4.1.0"
     log-symbols "4.1.0"
-    minimatch "3.0.4"
+    minimatch "5.0.1"
     ms "2.1.3"
-    nanoid "3.1.25"
+    nanoid "3.3.3"
     serialize-javascript "6.0.0"
     strip-json-comments "3.1.1"
     supports-color "8.1.1"
-    which "2.0.2"
-    workerpool "6.1.5"
+    workerpool "6.2.1"
     yargs "16.2.0"
     yargs-parser "20.2.4"
     yargs-unparser "2.0.0"
@@ -1007,10 +981,10 @@ ms@2.1.3:
   resolved "https://registry.yarnpkg.com/ms/-/ms-2.1.3.tgz#574c8138ce1d2b5861f0b44579dbadd60c6615b2"
   integrity sha512-6FlzubTLZG3J2a/NVCAleEhjzq5oxgHyaCU9yYXvcLsvoVaHJq/s5xXI6/XXP6tz7R9xAOtHnSO/tXtF3WRTlA==
 
-nanoid@3.1.25:
-  version "3.1.25"
-  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.1.25.tgz#09ca32747c0e543f0e1814b7d3793477f9c8e152"
-  integrity sha512-rdwtIXaXCLFAQbnfqDRnI6jaRHp9fTcYBjtFKE8eezcZ7LuLjhUaQGNeMXf1HmRoCH32CLz6XwX0TtxEOS/A3Q==
+nanoid@3.3.1:
+  version "3.3.1"
+  resolved "https://registry.yarnpkg.com/nanoid/-/nanoid-3.3.1.tgz#6347a18cac88af88f58af0b3594b723d5e99bb35"
+  integrity sha512-n6Vs/3KGyxPQd6uO0eH4Bv0ojGSUvuLlIHtC3Y0kEO23YRge8H9x1GCzLn28YX0H66pMkxuaeESFq4tKISKwdw==
 
 nanoid@3.3.3:
   version "3.3.3"
@@ -1045,7 +1019,7 @@ normalize-path@^3.0.0, normalize-path@~3.0.0:
 once@^1.3.0:
   version "1.4.0"
   resolved "https://registry.yarnpkg.com/once/-/once-1.4.0.tgz#583b1aa775961d4b113ac17d9c50baef9dd76bd1"
-  integrity sha1-WDsap3WWHUsROsF9nFC6753Xa9E=
+  integrity sha512-lNaJgI+2Q5URQBkccEKHTQOPaXdUxnZZElQTZY0MFUAuaEqe1E+Nyvgdz/aIyNi6Z9MzO5dv1H8n58/GELp3+w==
   dependencies:
     wrappy "1"
 
@@ -1076,17 +1050,17 @@ path-exists@^4.0.0:
 path-is-absolute@^1.0.0:
   version "1.0.1"
   resolved "https://registry.yarnpkg.com/path-is-absolute/-/path-is-absolute-1.0.1.tgz#174b9268735534ffbc7ace6bf53a5a9e1b5c5f5f"
-  integrity sha1-F0uSaHNVNP+8es5r9TpanhtcX18=
+  integrity sha512-AVbw3UJ2e9bq64vSaS9Am0fje1Pa8pbGqTTsmXfaIiMpnr5DlDhfJOuLj9Sf95ZPVDAUerDfEk88MPmPe7UCQg==
 
 pathval@^1.1.1:
   version "1.1.1"
   resolved "https://registry.yarnpkg.com/pathval/-/pathval-1.1.1.tgz#8534e77a77ce7ac5a2512ea21e0fdb8fcf6c3d8d"
   integrity sha512-Dp6zGqpTdETdR63lehJYPeIOqpiNBNtc7BpWSLrOje7UaIsE5aY92r/AunQA7rsXvet3lrJ3JnZX29UPTKXyKQ==
 
 picomatch@^2.0.4, picomatch@^2.2.1:
-  version "2.3.0"
-  resolved "https://registry.yarnpkg.com/picomatch/-/picomatch-2.3.0.tgz#f1f061de8f6a4bf022892e2d128234fb98302972"
-  integrity sha512-lY1Q/PiJGC2zOv/z391WOTD+Z02bCgsFfvxoXXf6h7kv9o+WmsmzYqrAwY63sNgOxE4xEdq0WyUnXfKeBrSvYw==
+  version "2.3.1"
+  resolved "https://registry.yarnpkg.com/picomatch/-/picomatch-2.3.1.tgz#3ba3833733646d9d3e4995946c1365a67fb07a42"
+  integrity sha512-JU3teHTNjmE2VCGFzuY8EXzCDVwEqB2a8fsIvwaStHhAWJEeVd1o1QD80CU6+ZdEXXSLbSsuLwJjkCBWqRQUVA==
 
 prettier@^2.5.1:
   version "2.5.1"
@@ -1115,7 +1089,7 @@ regenerator-runtime@^0.13.4:
 require-directory@^2.1.1:
   version "2.1.1"
   resolved "https://registry.yarnpkg.com/require-directory/-/require-directory-2.1.1.tgz#8c64ad5fd30dab1c976e2344ffe7f792a6a6df42"
-  integrity sha1-jGStX9MNqxyXbiNE/+f3kqam30I=
+  integrity sha512-fGxEI7+wsG9xrvdjsrlmL22OMTTiHRwAMroiEeMgq8gzoLC/PQr7RsRDSTLUg/bZAZtF+TVIkHc6/4RIKrui+Q==
 
 rpc-websockets@^7.5.0:
   version "7.5.0"
@@ -1348,10 +1322,10 @@ which@2.0.2:
   dependencies:
     isexe "^2.0.0"
 
-workerpool@6.1.5:
-  version "6.1.5"
-  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.1.5.tgz#0f7cf076b6215fd7e1da903ff6f22ddd1886b581"
-  integrity sha512-XdKkCK0Zqc6w3iTxLckiuJ81tiD/o5rBE/m+nXpRCB+/Sq4DqkfXZ/x0jW02DG1tGsfUGXbTJyZDP+eu67haSw==
+workerpool@6.2.0:
+  version "6.2.0"
+  resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.2.0.tgz#827d93c9ba23ee2019c3ffaff5c27fccea289e8b"
+  integrity sha512-Rsk5qQHJ9eowMH28Jwhe8HEbmdYDX4lwoMWshiCXugjtHqMD9ZbiqSDLxcsfdqsETPzVUtX5s1Z5kStiIM6l4A==
 
 workerpool@6.2.1:
   version "6.2.1"
@@ -1370,7 +1344,7 @@ wrap-ansi@^7.0.0:
 wrappy@1:
   version "1.0.2"
   resolved "https://registry.yarnpkg.com/wrappy/-/wrappy-1.0.2.tgz#b5243d8f3ec1aa35f1364605bc0d1036e30ab69f"
-  integrity sha1-tSQ9jz7BqjXxNkYFvA0QNuMKtp8=
+  integrity sha512-l4Sp/DRseor9wL6EvV2+TuQn63dMkPjZ/sp9XkghTEbV9KlPS1xUsZ3u7/IQO4wxtcFB4bgpQPRcR3QCvezPcQ==
 
 ws@^7.4.5:
   version "7.5.5"
```
