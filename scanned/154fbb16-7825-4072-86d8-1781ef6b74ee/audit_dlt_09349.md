# [?] chore: update deps to fix vulnerabilities (#7389)

## Summary
Severity: Unknown
Chain: Tooling
Component: web3/web3.js
Published: 2024-11-19
Source: https://github.com/web3/web3.js/commit/6229f4d8f0f0a327b00970a48702d191b64a6b49
Type: security-commit

## Details
chore: update deps to fix vulnerabilities (#7389)

## Patch
### yarn.lock
```diff
@@ -1210,7 +1210,7 @@
     "@jridgewell/set-array" "^1.0.0"
     "@jridgewell/sourcemap-codec" "^1.4.10"
 
-"@jridgewell/gen-mapping@^0.3.0", "@jridgewell/gen-mapping@^0.3.2":
+"@jridgewell/gen-mapping@^0.3.2":
   version "0.3.2"
   resolved "https://registry.yarnpkg.com/@jridgewell/gen-mapping/-/gen-mapping-0.3.2.tgz#c1aedc61e853f2bb9f5dfe6d4442d3b565b253b9"
   integrity sha512-mh65xKQAzI6iBcFzwv28KVWSmCkdRBWoOh+bYQGW3+6OZvbbN3TqMGo5hqYxQniRcH9F2VZIoJCm4pa3BPDK/A==
@@ -1219,6 +1219,15 @@
     "@jridgewell/sourcemap-codec" "^1.4.10"
     "@jridgewell/trace-mapping" "^0.3.9"
 
+"@jridgewell/gen-mapping@^0.3.5":
+  version "0.3.5"
+  resolved "https://registry.yarnpkg.com/@jridgewell/gen-mapping/-/gen-mapping-0.3.5.tgz#dcce6aff74bdf6dad1a95802b69b04a2fcb1fb36"
+  integrity sha512-IzL8ZoEDIBRWEzlCcRhOaCupYyN5gdIK+Q6fbFdPDg6HqX6jpkItn7DFIpW9LQzXG6Df9sA7+OKnq0qlz/GaQg==
+  dependencies:
+    "@jridgewell/set-array" "^1.2.1"
+    "@jridgewell/sourcemap-codec" "^1.4.10"
+    "@jridgewell/trace-mapping" "^0.3.24"
+
 "@jridgewell/resolve-uri@^3.0.3":
   version "3.1.0"
   resolved "https://registry.yarnpkg.com/@jridgewell/resolve-uri/-/resolve-uri-3.1.0.tgz#2203b118c157721addfe69d47b70465463066d78"
@@ -1234,13 +1243,18 @@
   resolved "https://registry.yarnpkg.com/@jridgewell/set-array/-/set-array-1.1.2.tgz#7c6cf998d6d20b914c0a55a91ae928ff25965e72"
   integrity sha512-xnkseuNADM0gt2bs+BvhO0p78Mk762YnZdsuzFV018NoG1Sj1SCQvpSqa7XUaTam5vAGasABV9qXASMKnFMwMw==
 
-"@jridgewell/source-map@^0.3.2":
-  version "0.3.2"
-  resolved "https://registry.yarnpkg.com/@jridgewell/source-map/-/source-map-0.3.2.tgz#f45351aaed4527a298512ec72f81040c998580fb"
-  integrity sha512-m7O9o2uR8k2ObDysZYzdfhb08VuEml5oWGiosa1VdaPZ/A6QyPkAJuwN0Q1lhULOf6B7MtQmHENS743hWtCrgw==
+"@jridgewell/set-array@^1.2.1":
+  version "1.2.1"
+  resolved "https://registry.yarnpkg.com/@jridgewell/set-array/-/set-array-1.2.1.tgz#558fb6472ed16a4c850b889530e6b36438c49280"
+  integrity sha512-R8gLRTZeyp03ymzP/6Lil/28tGeGEzhx1q2k703KGWRAI1VdvPIXdG70VJc2pAMw3NA6JKL5hhFu1sJX0Mnn/A==
+
+"@jridgewell/source-map@^0.3.3":
+  version "0.3.6"
+  resolved "https://registry.yarnpkg.com/@jridgewell/source-map/-/source-map-0.3.6.tgz#9d71ca886e32502eb9362c9a74a46787c36df81a"
+  integrity sha512-1ZJTZebgqllO79ue2bm3rIGud/bOe0pP5BjSRCRxxYkEZS8STV7zN84UBbiYu7jy+eCKSnVIUgoWWE/tt+shMQ==
   dependencies:
-    "@jridgewell/gen-mapping" "^0.3.0"
-    "@jridgewell/trace-mapping" "^0.3.9"
+    "@jridgewell/gen-mapping" "^0.3.5"
+    "@jridgewell/trace-mapping" "^0.3.25"
 
 "@jridgewell/sourcemap-codec@^1.4.10":
   version "1.4.14"
@@ -1260,7 +1274,7 @@
     "@jridgewell/resolve-uri" "^3.0.3"
     "@jridgewell/sourcemap-codec" "^1.4.10"
 
-"@jridgewell/trace-mapping@^0.3.12", "@jridgewell/trace-mapping@^0.3.14", "@jridgewell/trace-mapping@^0.3.9":
+"@jridgewell/trace-mapping@^0.3.12", "@jridgewell/trace-mapping@^0.3.9":
   version "0.3.15"
   resolved "https://registry.yarnpkg.com/@jridgewell/trace-mapping/-/trace-mapping-0.3.15.tgz#aba35c48a38d3fd84b37e66c9c0423f9744f9774"
   integrity sha512-oWZNOULl+UbhsgB51uuZzglikfIKSUBO/M9W2OfEjn7cmqoAiCgmv9lyACTUacZwBz0ITnJ2NqjU8Tx0DHL88g==
@@ -1284,6 +1298,14 @@
     "@jridgewell/resolve-uri" "^3.1.0"
     "@jridgewell/sourcemap-codec" "^1.4.14"
 
+"@jridgewell/trace-mapping@^0.3.20", "@jridgewell/trace-mapping@^0.3.24", "@jridgewell/trace-mapping@^0.3.25":
+  version "0.3.25"
+  resolved "https://registry.yarnpkg.com/@jridgewell/trace-mapping/-/trace-mapping-0.3.25.tgz#15f190e98895f3fc23276ee14bc76b675c2e50f0"
+  integrity sha512-vNk6aEwybGtawWmy/PzwnGDOjCkLWSD2wqvjGGAgOAwCGWySYXfYoxt00IJkTF+8Lb57DwOb3Aa0o9CApepiYQ==
+  dependencies:
+    "@jridgewell/resolve-uri" "^3.1.0"
+    "@jridgewell/sourcemap-codec" "^1.4.14"
+
 "@lerna/child-process@6.6.2":
   version "6.6.2"
   resolved "https://registry.yarnpkg.com/@lerna/child-process/-/child-process-6.6.2.tgz#5d803c8dee81a4e013dc428292e77b365cba876c"
@@ -2037,9 +2059,9 @@
     "@octokit/openapi-types" "^13.1.0"
 
 "@openzeppelin/contracts@^4.7.1":
-  version "4.9.3"
-  resolved "https://registry.yarnpkg.com/@openzeppelin/contracts/-/contracts-4.9.3.tgz#00d7a8cf35a475b160b3f0293a6403c511099364"
-  integrity sha512-He3LieZ1pP2TNt5JbkPA4PNT9WC3gOTOlDcFGJW4Le4QKqwmiNJCRt44APfxMxvq7OugU/cqYuPcSBzOw38DAg==
+  version "4.9.6"
+  resolved "https://registry.yarnpkg.com/@openzeppelin/contracts/-/contracts-4.9.6.tgz#2a880a24eb19b4f8b25adc2a5095f2aa27f39677"
+  integrity "sha1-KogKJOsZtPiyWtwqUJXyqifzlnc= sha512-xSmezSupL+y9VkHZJGDoCBpmnB2ogM13ccaYDWqJTfS3dbuHkgjuwDFUmaFauBCboQMGB/S5UqUl2y54X99BmA=="
 
 "@parcel/watcher@2.0.4":
   version "2.0.4"
@@ -2362,10 +2384,10 @@
   dependencies:
     "@types/node" "*"
 
-"@types/eslint-scope@^3.7.3":
-  version "3.7.4"
-  resolved "https://registry.yarnpkg.com/@types/eslint-scope/-/eslint-scope-3.7.4.tgz#37fc1223f0786c39627068a12e94d6e6fc61de16"
-  integrity sha512-9K4zoImiZc3HlIp6AVUDE4CWYx22a+lhSZMYNpbjW04+YF0KWj4pJXnEMjdnFTiQibFFmElcsasJXDbdI/EPhA==
+"@types/eslint-scope@^3.7.7":
+  version "3.7.7"
+  resolved "https://registry.yarnpkg.com/@types/eslint-scope/-/eslint-scope-3.7.7.tgz#3108bd5f18b0cdb277c867b3dd449c9ed7079ac5"
+  integrity "sha1-MQi9XxiwzbJ3yGez3UScntcHmsU= sha512-MzMFlSLBqNF2gcHWO0G1vP/YQyfvrxZ0bF+u7mzUdZ1/xK4A4sru+nraZz5i3iEIk1l1uyicaDVTB4QbbEkAYg=="
   dependencies:
     "@types/eslint" "*"
     "@types/estree" "*"
@@ -2383,10 +2405,10 @@
   resolved "https://registry.yarnpkg.com/@types/estree/-/estree-1.0.0.tgz#5fb2e536c1ae9bf35366eed879e827fa59ca41c2"
   integrity sha512-WulqXMDUTYAXCjZnk6JtIHPigp55cVtDgDrO2gHRwhyJto21+1zbVCtOYB2L1F9w4qCQ0rOGWBnBe0FNTiEJIQ==
 
-"@types/estree@^0.0.51":
-  version "0.0.51"
-  resolved "https://registry.yarnpkg.com/@types/estree/-/estree-0.0.51.tgz#cfd70924a25a3fd32b218e5e420e6897e1ac4f40"
-  integrity sha512-CuPgU6f3eT/XgKKPqKd/gLZV1Xmvf1a2R5POBOGQa6uv82xpls89HU5zKeVoyR8XzHd1RGNOlQlvUe3CFkjWNQ==
+"@types/estree@^1.0.6":
+  version "1.0.6"
+  resolved "https://registry.yarnpkg.com/@types/estree/-/estree-1.0.6.tgz#628effeeae2064a1b4e79f78e81d87b7e5fc7b50"
+  integrity sha512-AYnb1nQyY49te+VRAVgmzfcgjYS91mY5P0TKUDCLEM+gNnA+3T6rWITXRLYCpahpqSQbN5cE+gHpnPyXjHWxcw==
 
 "@types/express-serve-static-core@^4.17.18":
   version "4.17.30"
@@ -2719,125 +2741,125 @@
     "@typescript-eslint/types" "5.33.1"
     eslint-visitor-keys "^3.3.0"
 
-"@webassemblyjs/ast@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/ast/-/ast-1.11.1.tgz#2bfd767eae1a6996f432ff7e8d7fc75679c0b6a7"
-  integrity sha512-ukBh14qFLjxTQNTXocdyksN5QdM28S1CxHt2rdskFyL+xFV7VremuBLVbmCePj+URalXBENx/9Lm7lnhihtCSw==
+"@webassemblyjs/ast@1.14.1", "@webassemblyjs/ast@^1.12.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/ast/-/ast-1.14.1.tgz#a9f6a07f2b03c95c8d38c4536a1fdfb521ff55b6"
+  integrity "sha1-qfagfysDyVyNOMRTah/ftSH/VbY= sha512-nuBEDgQfm1ccRp/8bCQrx1frohyufl4JlbMMZ4P1wpeOfDhF6FQkxZJ1b/e+PLwr6X1Nhw6OLme5usuBWYBvuQ=="
   dependencies:
-    "@webassemblyjs/helper-numbers" "1.11.1"
-    "@webassemblyjs/helper-wasm-bytecode" "1.11.1"
+    "@webassemblyjs/helper-numbers" "1.13.2"
+    "@webassemblyjs/helper-wasm-bytecode" "1.13.2"
 
-"@webassemblyjs/floating-point-hex-parser@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/floating-point-hex-parser/-/floating-point-hex-parser-1.11.1.tgz#f6c61a705f0fd7a6aecaa4e8198f23d9dc179e4f"
-  integrity sha512-iGRfyc5Bq+NnNuX8b5hwBrRjzf0ocrJPI6GWFodBFzmFnyvrQ83SHKhmilCU/8Jv67i4GJZBMhEzltxzcNagtQ==
+"@webassemblyjs/floating-point-hex-parser@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/floating-point-hex-parser/-/floating-point-hex-parser-1.13.2.tgz#fcca1eeddb1cc4e7b6eed4fc7956d6813b21b9fb"
+  integrity "sha1-/Moe7dscxOe27tT8eVbWgTshufs= sha512-6oXyTOzbKxGH4steLbLNOu71Oj+C8Lg34n6CqRvqfS2O71BxY6ByfMDRhBytzknj9yGUPVJ1qIKhRlAwO1AovA=="
 
-"@webassemblyjs/helper-api-error@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-api-error/-/helper-api-error-1.11.1.tgz#1a63192d8788e5c012800ba6a7a46c705288fd16"
-  integrity sha512-RlhS8CBCXfRUR/cwo2ho9bkheSXG0+NwooXcc3PAILALf2QLdFyj7KGsKRbVc95hZnhnERon4kW/D3SZpp6Tcg==
+"@webassemblyjs/helper-api-error@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-api-error/-/helper-api-error-1.13.2.tgz#e0a16152248bc38daee76dd7e21f15c5ef3ab1e7"
+  integrity "sha1-4KFhUiSLw42u523X4h8Vxe86sec= sha512-U56GMYxy4ZQCbDZd6JuvvNV/WFildOjsaWD3Tzzvmw/mas3cXzRJPMjP83JqEsgSbyrmaGjBfDtV7KDXV9UzFQ=="
 
-"@webassemblyjs/helper-buffer@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-buffer/-/helper-buffer-1.11.1.tgz#832a900eb444884cde9a7cad467f81500f5e5ab5"
-  integrity sha512-gwikF65aDNeeXa8JxXa2BAk+REjSyhrNC9ZwdT0f8jc4dQQeDQ7G4m0f2QCLPJiMTTO6wfDmRmj/pW0PsUvIcA==
+"@webassemblyjs/helper-buffer@1.14.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-buffer/-/helper-buffer-1.14.1.tgz#822a9bc603166531f7d5df84e67b5bf99b72b96b"
+  integrity "sha1-giqbxgMWZTH31d+E5ntb+ZtyuWs= sha512-jyH7wtcHiKssDtFPRB+iQdxlDf96m0E39yb0k5uJVhFGleZFoNw1c4aeIcVUPPbXUVJ94wwnMOAqUHyzoEPVMA=="
 
-"@webassemblyjs/helper-numbers@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-numbers/-/helper-numbers-1.11.1.tgz#64d81da219fbbba1e3bd1bfc74f6e8c4e10a62ae"
-  integrity sha512-vDkbxiB8zfnPdNK9Rajcey5C0w+QJugEglN0of+kmO8l7lDb77AnlKYQF7aarZuCrv+l0UvqL+68gSDr3k9LPQ==
+"@webassemblyjs/helper-numbers@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-numbers/-/helper-numbers-1.13.2.tgz#dbd932548e7119f4b8a7877fd5a8d20e63490b2d"
+  integrity "sha1-29kyVI5xGfS4p4d/1ajSDmNJCy0= sha512-FE8aCmS5Q6eQYcV3gI35O4J789wlQA+7JrqTTpJqn5emA4U2hvwJmvFRC0HODS+3Ye6WioDklgd6scJ3+PLnEA=="
   dependencies:
-    "@webassemblyjs/floating-point-hex-parser" "1.11.1"
-    "@webassemblyjs/helper-api-error" "1.11.1"
+    "@webassemblyjs/floating-point-hex-parser" "1.13.2"
+    "@webassemblyjs/helper-api-error" "1.13.2"
     "@xtuc/long" "4.2.2"
 
-"@webassemblyjs/helper-wasm-bytecode@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-wasm-bytecode/-/helper-wasm-bytecode-1.11.1.tgz#f328241e41e7b199d0b20c18e88429c4433295e1"
-  integrity sha512-PvpoOGiJwXeTrSf/qfudJhwlvDQxFgelbMqtq52WWiXC6Xgg1IREdngmPN3bs4RoO83PnL/nFrxucXj1+BX62Q==
+"@webassemblyjs/helper-wasm-bytecode@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-wasm-bytecode/-/helper-wasm-bytecode-1.13.2.tgz#e556108758f448aae84c850e593ce18a0eb31e0b"
+  integrity "sha1-5VYQh1j0SKroTIUOWTzhig6zHgs= sha512-3QbLKy93F0EAIXLh0ogEVR6rOubA9AoZ+WRYhNbFyuB70j3dRdwH9g+qXhLAO0kiYGlg3TxDV+I4rQTr/YNXkA=="
 
-"@webassemblyjs/helper-wasm-section@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-wasm-section/-/helper-wasm-section-1.11.1.tgz#21ee065a7b635f319e738f0dd73bfbda281c097a"
-  integrity sha512-10P9No29rYX1j7F3EVPX3JvGPQPae+AomuSTPiF9eBQeChHI6iqjMIwR9JmOJXwpnn/oVGDk7I5IlskuMwU/pg==
+"@webassemblyjs/helper-wasm-section@1.14.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/helper-wasm-section/-/helper-wasm-section-1.14.1.tgz#9629dda9c4430eab54b591053d6dc6f3ba050348"
+  integrity "sha1-lindqcRDDqtUtZEFPW3G87oFA0g= sha512-ds5mXEqTJ6oxRoqjhWDU83OgzAYjwsCV8Lo/N+oRsNDmx/ZDpqalmrtgOMkHwxsG0iI//3BwWAErYRHtgn0dZw=="
   dependencies:
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/helper-buffer" "1.11.1"
-    "@webassemblyjs/helper-wasm-bytecode" "1.11.1"
-    "@webassemblyjs/wasm-gen" "1.11.1"
+    "@webassemblyjs/ast" "1.14.1"
+    "@webassemblyjs/helper-buffer" "1.14.1"
+    "@webassemblyjs/helper-wasm-bytecode" "1.13.2"
+    "@webassemblyjs/wasm-gen" "1.14.1"
 
-"@webassemblyjs/ieee754@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/ieee754/-/ieee754-1.11.1.tgz#963929e9bbd05709e7e12243a099180812992614"
-  integrity sha512-hJ87QIPtAMKbFq6CGTkZYJivEwZDbQUgYd3qKSadTNOhVY7p+gfP6Sr0lLRVTaG1JjFj+r3YchoqRYxNH3M0GQ==
+"@webassemblyjs/ieee754@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/ieee754/-/ieee754-1.13.2.tgz#1c5eaace1d606ada2c7fd7045ea9356c59ee0dba"
+  integrity "sha1-HF6qzh1gatosf9cEXqk1bFnuDbo= sha512-4LtOzh58S/5lX4ITKxnAK2USuNEvpdVV9AlgGQb8rJDHaLeHciwG4zlGr0j/SNWlr7x3vO1lDEsuePvtcDNCkw=="
   dependencies:
     "@xtuc/ieee754" "^1.2.0"
 
-"@webassemblyjs/leb128@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/leb128/-/leb128-1.11.1.tgz#ce814b45574e93d76bae1fb2644ab9cdd9527aa5"
-  integrity sha512-BJ2P0hNZ0u+Th1YZXJpzW6miwqQUGcIHT1G/sf72gLVD9DZ5AdYTqPNbHZh6K1M5VmKvFXwGSWZADz+qBWxeRw==
+"@webassemblyjs/leb128@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/leb128/-/leb128-1.13.2.tgz#57c5c3deb0105d02ce25fa3fd74f4ebc9fd0bbb0"
+  integrity "sha1-V8XD3rAQXQLOJfo/109OvJ/Qu7A= sha512-Lde1oNoIdzVzdkNEAWZ1dZ5orIbff80YPdHx20mrHwHrVNNTjNr8E3xz9BdpcGqRQbAEa+fkrCb+fRFTl/6sQw=="
   dependencies:
     "@xtuc/long" "4.2.2"
 
-"@webassemblyjs/utf8@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/utf8/-/utf8-1.11.1.tgz#d1f8b764369e7c6e6bae350e854dec9a59f0a3ff"
-  integrity sha512-9kqcxAEdMhiwQkHpkNiorZzqpGrodQQ2IGrHHxCy+Ozng0ofyMA0lTqiLkVs1uzTRejX+/O0EOT7KxqVPuXosQ==
-
-"@webassemblyjs/wasm-edit@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-edit/-/wasm-edit-1.11.1.tgz#ad206ebf4bf95a058ce9880a8c092c5dec8193d6"
-  integrity sha512-g+RsupUC1aTHfR8CDgnsVRVZFJqdkFHpsHMfJuWQzWU3tvnLC07UqHICfP+4XyL2tnr1amvl1Sdp06TnYCmVkA==
-  dependencies:
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/helper-buffer" "1.11.1"
-    "@webassemblyjs/helper-wasm-bytecode" "1.11.1"
-    "@webassemblyjs/helper-wasm-section" "1.11.1"
-    "@webassemblyjs/wasm-gen" "1.11.1"
-    "@webassemblyjs/wasm-opt" "1.11.1"
-    "@webassemblyjs/wasm-parser" "1.11.1"
-    "@webassemblyjs/wast-printer" "1.11.1"
-
-"@webassemblyjs/wasm-gen@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-gen/-/wasm-gen-1.11.1.tgz#86c5ea304849759b7d88c47a32f4f039ae3c8f76"
-  integrity sha512-F7QqKXwwNlMmsulj6+O7r4mmtAlCWfO/0HdgOxSklZfQcDu0TpLiD1mRt/zF25Bk59FIjEuGAIyn5ei4yMfLhA==
-  dependencies:
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/helper-wasm-bytecode" "1.11.1"
-    "@webassemblyjs/ieee754" "1.11.1"
-    "@webassemblyjs/leb128" "1.11.1"
-    "@webassemblyjs/utf8" "1.11.1"
-
-"@webassemblyjs/wasm-opt@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-opt/-/wasm-opt-1.11.1.tgz#657b4c2202f4cf3b345f8a4c6461c8c2418985f2"
-  integrity sha512-VqnkNqnZlU5EB64pp1l7hdm3hmQw7Vgqa0KF/KCNO9sIpI6Fk6brDEiX+iCOYrvMuBWDws0NkTOxYEb85XQHHw==
-  dependencies:
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/helper-buffer" "1.11.1"
-    "@webassemblyjs/wasm-gen" "1.11.1"
-    "@webassemblyjs/wasm-parser" "1.11.1"
-
-"@webassemblyjs/wasm-parser@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-parser/-/wasm-parser-1.11.1.tgz#86ca734534f417e9bd3c67c7a1c75d8be41fb199"
-  integrity sha512-rrBujw+dJu32gYB7/Lup6UhdkPx9S9SnobZzRVL7VcBH9Bt9bCBLEuX/YXOOtBsOZ4NQrRykKhffRWHvigQvOA==
-  dependencies:
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/helper-api-error" "1.11.1"
-    "@webassemblyjs/helper-wasm-bytecode" "1.11.1"
-    "@webassemblyjs/ieee754" "1.11.1"
-    "@webassemblyjs/leb128" "1.11.1"
-    "@webassemblyjs/utf8" "1.11.1"
-
-"@webassemblyjs/wast-printer@1.11.1":
-  version "1.11.1"
-  resolved "https://registry.yarnpkg.com/@webassemblyjs/wast-printer/-/wast-printer-1.11.1.tgz#d0c73beda8eec5426f10ae8ef55cee5e7084c2f0"
-  integrity sha512-IQboUWM4eKzWW+N/jij2sRatKMh99QEelo3Eb2q0qXkvPRISAj8Qxtmw5itwqK+TTkBuUIE45AxYPToqPtL5gg==
-  dependencies:
-    "@webassemblyjs/ast" "1.11.1"
+"@webassemblyjs/utf8@1.13.2":
+  version "1.13.2"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/utf8/-/utf8-1.13.2.tgz#917a20e93f71ad5602966c2d685ae0c6c21f60f1"
+  integrity "sha1-kXog6T9xrVYClmwtaFrgxsIfYPE= sha512-3NQWGjKTASY1xV5m7Hr0iPeXD9+RDobLll3T9d2AO+g3my8xy5peVyjSag4I50mR1bBSN/Ct12lo+R9tJk0NZQ=="
+
+"@webassemblyjs/wasm-edit@^1.12.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-edit/-/wasm-edit-1.14.1.tgz#ac6689f502219b59198ddec42dcd496b1004d597"
+  integrity "sha1-rGaJ9QIhm1kZjd7ELc1JaxAE1Zc= sha512-RNJUIQH/J8iA/1NzlE4N7KtyZNHi3w7at7hDjvRNm5rcUXa00z1vRz3glZoULfJ5mpvYhLybmVcwcjGrC1pRrQ=="
+  dependencies:
+    "@webassemblyjs/ast" "1.14.1"
+    "@webassemblyjs/helper-buffer" "1.14.1"
+    "@webassemblyjs/helper-wasm-bytecode" "1.13.2"
+    "@webassemblyjs/helper-wasm-section" "1.14.1"
+    "@webassemblyjs/wasm-gen" "1.14.1"
+    "@webassemblyjs/wasm-opt" "1.14.1"
+    "@webassemblyjs/wasm-parser" "1.14.1"
+    "@webassemblyjs/wast-printer" "1.14.1"
+
+"@webassemblyjs/wasm-gen@1.14.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-gen/-/wasm-gen-1.14.1.tgz#991e7f0c090cb0bb62bbac882076e3d219da9570"
+  integrity "sha1-mR5/DAkMsLtiu6yIIHbj0hnalXA= sha512-AmomSIjP8ZbfGQhumkNvgC33AY7qtMCXnN6bL2u2Js4gVCg8fp735aEiMSBbDR7UQIj90n4wKAFUSEd0QN2Ukg=="
+  dependencies:
+    "@webassemblyjs/ast" "1.14.1"
+    "@webassemblyjs/helper-wasm-bytecode" "1.13.2"
+    "@webassemblyjs/ieee754" "1.13.2"
+    "@webassemblyjs/leb128" "1.13.2"
+    "@webassemblyjs/utf8" "1.13.2"
+
+"@webassemblyjs/wasm-opt@1.14.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-opt/-/wasm-opt-1.14.1.tgz#e6f71ed7ccae46781c206017d3c14c50efa8106b"
+  integrity "sha1-5vce18yuRngcIGAX08FMUO+oEGs= sha512-PTcKLUNvBqnY2U6E5bdOQcSM+oVP/PmrDY9NzowJjislEjwP/C4an2303MCVS2Mg9d3AJpIGdUFIQQWbPds0Sw=="
+  dependencies:
+    "@webassemblyjs/ast" "1.14.1"
+    "@webassemblyjs/helper-buffer" "1.14.1"
+    "@webassemblyjs/wasm-gen" "1.14.1"
+    "@webassemblyjs/wasm-parser" "1.14.1"
+
+"@webassemblyjs/wasm-parser@1.14.1", "@webassemblyjs/wasm-parser@^1.12.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/wasm-parser/-/wasm-parser-1.14.1.tgz#b3e13f1893605ca78b52c68e54cf6a865f90b9fb"
+  integrity "sha1-s+E/GJNgXKeLUsaOVM9qhl+Qufs= sha512-JLBl+KZ0R5qB7mCnud/yyX08jWFw5MsoalJ1pQ4EdFlgj9VdXKGuENGsiCIjegI1W7p91rUlcB/LB5yRJKNTcQ=="
+  dependencies:
+    "@webassemblyjs/ast" "1.14.1"
+    "@webassemblyjs/helper-api-error" "1.13.2"
+    "@webassemblyjs/helper-wasm-bytecode" "1.13.2"
+    "@webassemblyjs/ieee754" "1.13.2"
+    "@webassemblyjs/leb128" "1.13.2"
+    "@webassemblyjs/utf8" "1.13.2"
+
+"@webassemblyjs/wast-printer@1.14.1":
+  version "1.14.1"
+  resolved "https://registry.yarnpkg.com/@webassemblyjs/wast-printer/-/wast-printer-1.14.1.tgz#3bb3e9638a8ae5fdaf9610e7a06b4d9f9aa6fe07"
+  integrity "sha1-O7PpY4qK5f2vlhDnoGtNn5qm/gc= sha512-kPSSXE6De1XOR820C90RIo2ogvZG+c3KiHzqUoO/F34Y2shGzesfqv7o57xrxovZJH/MetF5UjroJ/R/3isoiw=="
+  dependencies:
+    "@webassemblyjs/ast" "1.14.1"
     "@xtuc/long" "4.2.2"
 
 "@webpack-cli/configtest@^1.2.0":
@@ -2982,11 +3004,6 @@ acorn-globals@^7.0.0:
     acorn "^8.1.0"
     acorn-walk "^8.0.2"
 
-acorn-import-assertions@^1.7.6:
-  version "1.8.0"
-  resolved "https://registry.yarnpkg.com/acorn-import-assertions/-/acorn-import-assertions-1.8.0.tgz#ba2b5939ce62c238db6d93d81c9b111b29b855e9"
-  integrity sha512-m7VZ3jwz4eK6A4Vtt8Ew1/mNbP24u0FhdyfA7fSvnJR6LMdfOYnmuIrrJAgrYfYJ10F/otaHTtrtrtmHdMNzEw==
-
 acorn-jsx@^5.3.2:
   version "5.3.2"
   resolved "https://registry.yarnpkg.com/acorn-jsx/-/acorn-jsx-5.3.2.tgz#7ed5bb55908b3b2f1bc55c6af1653bada7f07937"
@@ -2997,7 +3014,7 @@ acorn-walk@^8.0.0, acorn-walk@^8.0.2, acorn-walk@^8.1.1:
   resolved "https://registry.yarnpkg.com/acorn-walk/-/acorn-walk-8.2.0.tgz#741210f2e2426454508853a2f44d0ab83b7f69c1"
   integrity sha512-k+iyHEuPgSw6SbuDpGQM+06HQUa04DZ3o+F6CSzXMvvI5KMvnaEqXe+YVe555R9nn6GPt404fos4wcgpw12SDA==
 
-acorn@^8.0.4, acorn@^8.4.1, acorn@^8.5.0, acorn@^8.7.1, acorn@^8.8.0:
+acorn@^8.0.4, acorn@^8.4.1, acorn@^8.8.0:
   version "8.8.2"
   resolved "https://registry.yarnpkg.com/acorn/-/acorn-8.8.2.tgz#1b2f25db02af965399b9776b0c2c391276d37c4a"
   integrity sha512-xjIYgE8HBrkpd/sJqOGNspf8uHG+NOHGOw6a/Urj8taM2EXfdNAH2oFcPeIFfsv3+kz/mJrS5VuMqbNLjCa2vw==
@@ -3007,6 +3024,11 @@ acorn@^8.1.0, acorn@^8.8.1:
   resolved "https://registry.yarnpkg.com/acorn/-/acorn-8.10.0.tgz#8be5b3907a67221a81ab23c7889c4c5526b62ec5"
   integrity sha512-F0SAmZ8iUtS//m8DmCTA0jlh6TDKkHQyK6xc6V4KDTyZKA9dnvX9/3sRTVQrWm79glUAZbnmmNcdYwUIHWVybw==
 
+acorn@^8.14.0, acorn@^8.8.2:
+  version "8.14.0"
+  resolved "https://registry.yarnpkg.com/acorn/-/acorn-8.14.0.tgz#063e2c70cac5fb4f6467f0b11152e04c682795b0"
+  integrity sha512-cl669nCJTZBsL97OF4kUQm5g5hC2uihk0NxY3WENAC0TYdILVkAyHymAntgxGkl7K+t0cXIrH5siy5S4XkFycA==
+
 add-stream@^1.0.0:
   version "1.0.0"
   resolved "https://registry.yarnpkg.com/add-stream/-/add-stream-1.0.0.tgz#6a7990437ca736d5e1288db92bd3266d5f5cb2aa"
@@ -3651,14 +3673,7 @@ braces@^2.3.1:
     split-string "^3.0.2"
     to-regex "^3.0.1"
 
-braces@^3.0.2, braces@~3.0.2:
-  version "3.0.2"
-  resolved "https://registry.yarnpkg.com/braces/-/braces-3.0.2.tgz#3454e1a462ee8d599e236df336cd9ea4f8afe107"
-  integrity sha512-b8um+L1RzM3WDSzvhm6gIz1yfTbBt6YTlcEKAvsmqCZZFw46z626lVj9j1yEPW33H5H+lBQpZMP1k8l+78Ha0A==
-  dependencies:
-    fill-range "^7.0.1"
-
-braces@^3.0.3:
+braces@^3.0.3, braces@~3.0.2:
   version "3.0.3"
   resolved "https://registry.yarnpkg.com/braces/-/braces-3.0.3.tgz#490332f40919452272d55a8480adc0c441358789"
   integrity sha512-yQbXgO/OSZVD2IsiLlro+7Hf6Q18EJrKSEsdoMzKePKXct3gvD8oLcOQdIzGupr5Fj+EDe8gO/lxc1BzfMpxvA==
@@ -3697,7 +3712,7 @@ browserify-aes@^1.2.0:
     inherits "^2.0.1"
     safe-buffer "^5.0.1"
 
-browserslist@^4.14.5, browserslist@^4.20.2, browserslist@^4.21.3:
+browserslist@^4.20.2, browserslist@^4.21.3:
   version "4.21.3"
   resolved "https://registry.yarnpkg.com/browserslist/-/browserslist-4.21.3.tgz#5df277694eb3c48bc5c4b05af3e8b7e09c5a6d1a"
   integrity sha512-898rgRXLAyRkM1GryrrBHGkqA5hlpkV5MhtZwg9QXeiyLUYs2k00Un05aX5l2/yJIOObYKOpS2JNo8nJDE7fWQ==
@@ -3707,6 +3722,16 @@ browserslist@^4.14.5, browserslist@^4.20.2, browserslist@^4.21.3:
     node-releases "^2.0.6"
     update-browserslist-db "^1.0.5"
 
+browserslist@^4.24.0:
+  version "4.24.2"
+  resolved "https://registry.yarnpkg.com/browserslist/-/browserslist-4.24.2.tgz#f5845bc91069dbd55ee89faf9822e1d885d16580"
+  integrity sha512-ZIc+Q62revdMcqC6aChtW4jz3My3klmCO1fEmINZY/8J3EpBg5/A/D0AKmBveUh6pgoeycoMkVMko84tuYS+Gg==
+  dependencies:
+    caniuse-lite "^1.0.30001669"
+    electron-to-chromium "^1.5.41"
+    node-releases "^2.0.18"
+    update-browserslist-db "^1.1.1"
+
 bs-logger@0.x:
   version "0.2.6"
   resolved "https://registry.yarnpkg.com/bs-logger/-/bs-logger-0.2.6.tgz#eb7d365307a72cf974cc6cda76b68354ad336bd8"
@@ -3916,6 +3941,11 @@ caniuse-lite@^1.0.30001370:
   resolved "https://registry.yarnpkg.com/caniuse-lite/-/caniuse-lite-1.0.30001378.tgz#3d2159bf5a8f9ca093275b0d3ecc717b00f27b67"
   integrity sha512-JVQnfoO7FK7WvU4ZkBRbPjaot4+YqxogSDosHv0Hv5mWpUESmN+UubMU6L/hGz8QlQ2aY5U0vR6MOs6j/CXpNA==
 
+caniuse-lite@^1.0.30001669:
+  version "1.0.30001680"
+  resolved "https://registry.yarnpkg.com/caniuse-lite/-/caniuse-lite-1.0.30001680.tgz#5380ede637a33b9f9f1fc6045ea99bd142f3da5e"
+  integrity "sha1-U4Dt5jejO5+fH8YEXqmb0ULz2l4= sha512-rPQy70G6AGUMnbwS1z6Xg+RkHYPAi18ihs47GH0jcxIG7wArmPgY3XbS2sRdBbxJljp3thdT8BIqv9ccCypiPA=="
+
 case@^1.6.3:
   version "1.6.3"
   resolved "https://registry.yarnpkg.com/case/-/case-1.6.3.tgz#0a4386e3e9825351ca2e6216c60467ff5f1ea1c9"
@@ -4692,9 +4722,9 @@ declaration-bundler-webpack-plugin@^1.0.3:
   integrity sha512-bgeoSOZYTOOdiNUZd/U8K6Z+6IrM/X+DgUcm3/VI1l130lzOBeL+ObetjIkKksxcj0zUJbLaFRFumFGYDOQ9fg==
 
 decode-uri-component@^0.2.0:
-  version "0.2.0"
-  resolved "https://registry.yarnpkg.com/decode-uri-component/-/decode-uri-component-0.2.0.tgz#eb3913333458775cb84cd1a1fae062106bb87545"
-  integrity sha512-hjf+xovcEn31w/EUYdTXQh/8smFL/dzYjohQGEIgjyNavaJfBY2p5F527Bo1VPATxv0VYTUC2bOcXvqFwk78Og==
+  version "0.2.2"
+  resolved "https://registry.yarnpkg.com/decode-uri-component/-/decode-uri-component-0.2.2.tgz#e69dbe25d37941171dd540e024c444cd5188e1e9"
+  integrity "sha1-5p2+JdN5QRcd1UDgJMREzVGI4ek= sha512-FqUYQ+8o158GyGTrMFJms9qh3CqTKvAqgqsTnkLI8sKu0028orqBhxNMFkFen0zGyg6epACD32pjVk58ngIErQ=="
 
 dedent@0.7.0, dedent@^0.7.0:
   version "0.7.0"
@@ -4965,9 +4995,9 @@ ee-first@1.1.1:
   integrity sha512-WMwm9LhRUo+WUaRN+vRuETqG89IgZphVSNkdFgeb6sS/E4OrDIN7t48CAewSHXc6C8lefD8KKfr5vY61brQlow==
 
 ejs@^3.1.7:
-  version "3.1.9"
-  resolved "https://registry.yarnpkg.com/ejs/-/ejs-3.1.9.tgz#03c9e8777fe12686a9effcef22303ca3d8eeb361"
-  integrity sha512-rC+QVNMJWv+MtPgkt0y+0rVEIdbtxVADApW9JXrUVlzHetgcyczP/E7DJmWJ4fJCZF2cPcBk0laWO9ZHMG3DmQ==
+  version "3.1.10"
+  resolved "https://registry.yarnpkg.com/ejs/-/ejs-3.1.10.tgz#69ab8358b14e896f80cc39e62087b88500c3ac3b"
+  integrity sha512-UeJmFfOrAQS8OJWPZ4qtgHyWExa088/MtK5UEyoJGFH67cDEXkZSviOiKRCZ4Xij0zxI3JECgYs3oKx+AizQBA==
   dependencies:
     jake "^10.8.5"
 
@@ -4976,6 +5006,11 @@ electron-to-chromium@^1.4.202:
   resolved "https://registry.yarnpkg.com/electron-to-chromium/-/electron-to-chromium-1.4.222.tgz#2ba24bef613fc1985dbffea85df8f62f2dec6448"
   integrity sha512-gEM2awN5HZknWdLbngk4uQCVfhucFAfFzuchP3wM3NN6eow1eDU0dFy2kts43FB20ZfhVFF0jmFSTb1h5OhyIg==
 
+electron-to-chromium@^1.5.41:
+  version "1.5.58"
+  resolved "https://registry.yarnpkg.com/electron-to-chromium/-/electron-to-chromium-1.5.58.tgz#d90bd7a04d9223dce4e72316e14492140ec9af40"
+  integrity "sha1-2QvXoE2SI9zk5yMW4USSFA7Jr0A= sha512-al2l4r+24ZFL7WzyPTlyD0fC33LLzvxqLCwurtBibVPghRGO9hSTl+tis8t1kD7biPiH/en4U0I7o/nQbYeoVA=="
+
 elliptic@6.5.4, elliptic@^6.5.2, elliptic@^6.5.4:
   version "6.5.4"
   resolved "https://registry.yarnpkg.com/elliptic/-/elliptic-6.5.4.tgz#da37cebd31e79a1367e941b592ed1fbebd58abbb"
@@ -5043,7 +5078,7 @@ end-of-stream@^1.4.1:
   dependencies:
     once "^1.4.0"
 
-enhanced-resolve@^5.0.0, enhanced-resolve@^5.10.0:
+enhanced-resolve@^5.0.0:
   version "5.10.0"
   resolved "https://registry.yarnpkg.com/enhanced-resolve/-/enhanced-resolve-5.10.0.tgz#0dc579c3bb2a1032e357ac45b8f3a6f3ad4fb1e6"
   integrity sha512-T0yTFjdpldGY8PmuXXR0PyQ1ufZpEGiHVrp7zHKB7jdR4qlmZHhONVM5AQOAWXuF/w3dnHbEQVrNptJgt7F+cQ==
@@ -5059,6 +5094,14 @@ enhanced-resolve@^5.12.0:
     graceful-fs "^4.2.4"
     tapable "^2.2.0"
 
+enhanced-resolve@^5.17.1:
+  version "5.17.1"
+  resolved "https://registry.yarnpkg.com/enhanced-resolve/-/enhanced-resolve-5.17.1.tgz#67bfbbcc2f81d511be77d686a90267ef7f898a15"
+  integrity sha512-LMHl3dXhTcfv8gM4kEzIUeTQ+7fpdA0l2tUf34BddXPkz2A5xJ5L/Pchd5BL6rdccM9QGvu0sWZzK1Z1t4wwyg==
+  dependencies:
+    graceful-fs "^4.2.4"
+    tapable "^2.2.0"
+
 enquirer@^2.3.0, enquirer@~2.3.6:
   version "2.3.6"
   resolved "https://registry.yarnpkg.com/enquirer/-/enquirer-2.3.6.tgz#2a7fe5dd634a1e4125a975ec994ff5456dc3734d"
@@ -5146,10 +5189,10 @@ es-errors@^1.3.0:
   resolved "https://registry.yarnpkg.com/es-errors/-/es-errors-1.3.0.tgz#05f75a25dab98e4fb1dcd5e1472c0546d5057c8f"
   integrity sha512-Zf5H2Kxt2xjTvbJvP2ZWLEICxA6j+hAmMzIlypy4xcBg1vKVnx89Wy0GbS+kf5cwCVFFzdCFh2XSCFNULS6csw==
 
-es-module-lexer@^0.9.0:
-  version "0.9.3"
-  resolved "https://registry.yarnpkg.com/es-module-lexer/-/es-module-lexer-0.9.3.tgz#6f13db00cc38417137daf74366f535c8eb438f19"
-  integrity sha512-1HQ2M2sPtxwnvOvT1ZClHyQDiggdNjURWpY2we6aMKCQiUVxTmVs2UYPLIrD84sS+kMdUwfBSylbJPwNnBrnHQ==
+es-module-lexer@^1.2.1:
+  version "1.5.4"
+  resolved "https://registry.yarnpkg.com/es-module-lexer/-/es-module-lexer-1.5.4.tgz#a8efec3a3da991e60efa6b633a7cad6ab8d26b78"
+  integrity sha512-MVNK56NiMrOwitFB7cqDwq0CQutbw+0BvLshJSse0MUNU+y1FC3bUS/AQg7oUng+/wKrrki7JfmwtVHkVfPLlw==
 
 es-shim-unscopables@^1.0.0:
   version "1.0.0"
@@ -5177,6 +5220,11 @@ escalade@^3.1.1:
   resolved "https://registry.yarnpkg.com/escalade/-/escalade-3.1.1.tgz#d8cfdc7000965c5a0174b4a82eaa5c0552742e40"
   integrity sha512-k0er2gUkLf8O0zKJiAhmkTnJlTvINGv7ygDNPbeIsX/TJjGJZHuh9B2UxbsaEkmlEo9MfhrSzmhIlhRlI2GXnw==
 
+escalade@^3.2.0:
+  version "3.2.0"
+  resolved "https://registry.yarnpkg.com/escalade/-/escalade-3.2.0.tgz#011a3f69856ba189dffa7dc8fcce99d2a87903e5"
+  integrity sha512-WUj2qlxaQtO4g6Pq5c29GTcWGDyd8itL8zTlipgECz3JesAiiOKotd8JU6otB3PACgG6xkJUyVhboMS+bje/jA==
+
 escape-html@~1.0.3:
   version "1.0.3"
   resolved "https://registry.yarnpkg.com/escape-html/-/escape-html-1.0.3.tgz#0258eae4d3d0c0974de1c169188ef0051d1d1988"
@@ -6114,13 +6162,6 @@ fill-range@^4.0.0:
     repeat-string "^1.6.1"
     to-regex-range "^2.1.0"
 
-fill-range@^7.0.1:
-  version "7.0.1"
-  resolved "https://registry.yarnpkg.com/fill-range/-/fill-range-7.0.1.tgz#1919a6a7c75fe38b2c7c77e5198535da9acdda40"
-  integrity sha512-qOo9F+dMUmC2Lcb4BbVvnKJxTPjCm+RRpe4gDuGrzkL7mEVl/djYSu2OdQ2Pa302N4oqkSg9ir6jaLWJ2USVpQ==
-  dependencies:
-    to-regex-range "^5.0.1"
-
 fill-range@^7.1.1:
   version "7.1.1"
   resolved "https://registry.yarnpkg.com/fill-range/-/fill-range-7.1.1.tgz#44265d3cac07e3ea7dc247516380643754a05292"
@@ -6188,9 +6229,9 @@ flatted@^3.3.1:
   integrity sha512-X8cqMLLie7KsNUDSdzeN8FYK9rEt4Dt67OsG/DNGnYTSDBG4uFAJFBnUeiV+zCVAvwFy56IjM9sH51jVaEhNxw==
 
 follow-redirects@^1.0.0, follow-redirects@^1.12.1:
-  version "1.15.1"
-  resolved "https://registry.yarnpkg.com/follow-redirects/-/follow-redirects-1.15.1.tgz#0ca6a452306c9b276e4d3127483e29575e207ad5"
-  integrity sha512-yLAMQs+k0b2m7cVxpS1VKJVvoz7SS9Td1zss3XRwXj+ZDH00RJgnuLx7E44wx02kQLrdM3aOOy+FpzS7+8OizA==
+  version "1.15.9"
+  resolved "https://registry.yarnpkg.com/follow-redirects/-/follow-redirects-1.15.9.tgz#a604fa10e443bf98ca94228d9eebcc2e8a2c8ee1"
+  integrity sha512-gew4GsXizNgdoRyqmyfMHyAmXsZDk6mHkSxZFCzW9gwlbtOW44CDtYavM+y+72qD/Vq2l550kMF52DT8fOLJqQ==
 
 follow-redirects@^1.15.6:
   version "1.15.6"
@@ -6743,6 +6784,11 @@ graceful-fs@4.2.10, graceful-fs@^4.1.11, graceful-fs@^4.1.15, graceful-fs@^4.1.2
   resolved "https://registry.yarnpkg.com/graceful-fs/-/graceful-fs-4.2.10.tgz#147d3a006da4ca3ce14728c7aefc287c367d7a6c"
   integrity sha512-9ByhssR2fPVsNZj478qUUbKfmL0+t5BDVyjShtyZZLiK7ZDAArFFfopyOTj0M05wE2tJPisA4iTnnXl2YoPvOA==
 
+graceful-fs@^4.2.11:
+  version "4.2.11"
+  resolved "https://registry.yarnpkg.com/graceful-fs/-/graceful-fs-4.2.11.tgz#4183e4e8bf08bb6e05bbb2f7d2e0c8f712ca40e3"
+  integrity sha512-RbJ5/jmFcNNCcDV5o9eTnBLJ/HszWV0P73bc+Ff4nS/rJj+YaS6IGyiOL0VoBYX+l1Wrl3k63h/KrH+nhJ0XvQ==
+
 grapheme-splitter@^1.0.4:
   version "1.0.4"
   resolved "https://registry.yarnpkg.com/grapheme-splitter/-/grapheme-splitter-1.0.4.tgz#9cf3a665c6247479896834af35cf1dbb4400767e"
@@ -7019,12 +7065,7 @@ http-browserify@^1.7.0:
     Base64 "~0.2.0"
     inherits "~2.0.1"
 
-http-cache-semantics@^4.1.0:
-  version "4.1.0"
-  resolved "https://registry.yarnpkg.com/http-cache-semantics/-/http-cache-semantics-4.1.0.tgz#49e91c5cbf36c9b94bcfcd71c23d5249ec74e390"
-  integrity sha512-carPklcUh7ROWRK7Cv27RPtdhYhUsela/ue5/jKzjegVvXDqM2ILE9Q2BGn9JZJh1g87cp56su/FgQSzcWS8cQ==
-
-http-cache-semantics@^4.1.1:
+http-cache-semantics@^4.1.0, http-cache-semantics@^4.1.1:
   version "4.1.1"
   resolved "https://registry.yarnpkg.com/http-cache-semantics/-/http-cache-semantics-4.1.1.tgz#abe02fcb2985460bf0323be664436ec3476a6d5a"
   integrity sha512-er295DKPVsV82j5kw1Gjt+ADA/XYHsajl82cGNQG2eyoPkvgUhX+nDIyelzhIWbbsXP39EHcI6l5tYs2FYqYXQ==
@@ -8465,9 +8506,9 @@ json-stringify-safe@^5.0.1, json-stringify-safe@~5.0.1:
   integrity sha512-ZClg6AaYvamvYEE82d3Iyd3vSSIjQ+odgjaTzRuO3s7toCdFKczob2i0zCh7JE8kWn17yvAWhUVxvqGwUalsRA==
 
 json5@^1.0.1:
-  version "1.0.1"
-  resolved "https://registry.yarnpkg.com/json5/-/json5-1.0.1.tgz#779fb0018604fa854eacbf6252180d83543e3dbe"
-  integrity sha512-aKS4WQjPenRxiQsC93MNfjx+nbF4PAdYzmd/1JIj8HYzqfbu86beTuNgXDzPknWk0n0uARlyewZo4s++ES36Ow==
+  version "1.0.2"
+  resolved "https://registry.yarnpkg.com/json5/-/json5-1.0.2.tgz#63d98d60f21b313b77c4d6da18bfa69d80e1d593"
+  integrity sha512-g1MWMLBiz8FKi1e4w0UyVL3w+iJceWAFBAaBnnGKOpNa5f8TLktkbre1+s6oICydWAm+HRUGTmI+//xv2hvXYA==
   dependencies:
     minimist "^1.2.0"
 
@@ -9180,15 +9221,7 @@ micromatch@^3.1.10:
     snapdragon "^0.8.1"
     to-regex "^3.0.2"
 
-micromatch@^4.0.0, micromatch@^4.0.2, micromatch@^4.0.4:
-  version "4.0.5"
-  resolved "https://registry.yarnpkg.com/micromatch/-/micromatch-4.0.5.tgz#bc8999a7cbbf77cdc89f132f6e467051b49090c6"
-  integrity sha512-DMy+ERcEW2q8Z2Po+WNXuw3c5YaUSFjAO5GsJqfEl7UjvtIuFKO6ZrKvcItdy98dwFI2N1tg3zNIdKaQT+aNdA==
-  dependencies:
-    braces "^3.0.2"
-    picomatch "^2.3.1"
-
-micromatch@~4.0.7:
+micromatch@^4.0.0, micromatch@^4.0.2, micromatch@^4.0.4, micromatch@~4.0.7:
   version "4.0.8"
   resolved "https://registry.yarnpkg.com/micromatch/-/micromatch-4.0.8.tgz#d66fa18f3a47076789320b9b1af32bd86d9fa202"
   integrity sha512-PXwfBhYu0hBCPw8Dn0E+WDYb7af3dSLVWKi3HGv84IdF4TyFoC0ysxFd0Goxw7nSv4T/PzEJQxsYsEiFCKo2BA==
@@ -9607,6 +9640,11 @@ node-int64@^0.4.0:
   resolved "https://registry.yarnpkg.com/node-int64/-/node-int64-0.4.0.tgz#87a9065cdb355d3182d8f94ce11188b825c68a3b"
   integrity sha512-O5lz91xSOeoXP6DulyHfllpq+Eg00MWitZIbtPfoSEvqIHdl5gfcY6hYzDWnj0qD5tz52PI08u9qUvSVeUBeHw==
 
+node-releases@^2.0.18:
+  version "2.0.18"
+  resolved "https://registry.yarnpkg.com/node-releases/-/node-releases-2.0.18.tgz#f010e8d35e2fe8d6b2944f03f70213ecedc4ca3f"
+  integrity sha512-d9VeXT4SJ7ZeOqGX6R5EM022wpL+eWPooLI+5UpWn2jCT1aosUQEhQP214x33Wkwx3JQMvIm+tIoVOdodFS40g==
+
 node-releases@^2.0.6:
   version "2.0.6"
   resolved "https://registry.yarnpkg.com/node-releases/-/node-releases-2.0.6.tgz#8a7088c63a55e493845683ebf3c828d8c51c5503"
@@ -10442,6 +10480,11 @@ picocolors@^1.0.0:
   resolved "https://registry.yarnpkg.com/picocolors/-/picocolors-1.0.0.tgz#cb5bdc74ff3f51892236eaf79d68bc44564ab81c"
   integrity sha512-1fygroTLlHu66zi26VoTDv8yRgm0Fccecssto+MhsZ0D/DGW2sm8E8AjW7NU5VVTRt5GxbeZ5qBuJr+HyLYkjQ==
 
+picocolors@^1.1.0:
+  version "1.1.1"
+  resolved "https://registry.yarnpkg.com/picocolors/-/picocolors-1.1.1.tgz#3d321af3eab939b083c8f929a1d12cda81c26b6b"
+  integrity sha512-xceH2snhtb5M9liqDsmEw56le376mTZkEX/jEb/RxNFyegNul7eNslCXP9FDj/Lcu0X8KEyMceP2ntpaHrDEVA==
+
 picomatch@^2.0.4, picomatch@^2.2.1, picomatch@^2.2.3, picomatch@^2.3.1:
   version "2.3.1"
   resolved "https://registry.yarnpkg.com/picomatch/-/picomatch-2.3.1.tgz#3ba3833733646d9d3e4995946c1365a67fb07a42"
@@ -11234,7 +11277,7 @@ saxes@^6.0.0:
   dependencies:
     xmlchars "^2.2.0"
 
-schema-utils@^3.1.0, schema-utils@^3.1.1:
+schema-utils@^3.1.1:
   version "3.1.1"
   resolved "https://registry.yarnpkg.com/schema-utils/-/schema-utils-3.1.1.tgz#bc74c4b6b6995c1d88f76a8b77bea7219e0c8281"
   integrity sha512-Y5PQxS4ITlC+EahLuXaY86TXfR7Dc5lw294alXOq86JAHCihAIZfqv8nNCWvaEJvaC51uN9hbLGeV0cFBdH+Fw==
@@ -11243,6 +11286,15 @@ schema-utils@^3.1.0, schema-utils@^3.1.1:
     ajv "^6.12.5"
     ajv-keywords "^3.5.2"
 
+schema-utils@^3.2.0:
+  version "3.3.0"
+  resolved "https://registry.yarnpkg.com/schema-utils/-/schema-utils-3.3.0.tgz#f50a88877c3c01652a15b622ae9e9795df7a60fe"
+  integrity sha512-pN/yOAvcC+5rQ5nERGuwrjLlYvLTbCibnZ1I7B1LaiAz9BRBlE9GMgE/eqV30P7aJQUf7Ddimy/RsbYO/GrVGg==
+  dependencies:
+    "@types/json-schema" "^7.0.8"
+    ajv "^6.12.5"
+    ajv-keywords "^3.5.2"
+
 scrypt-js@3.0.1, scrypt-js@^3.0.0, scrypt-js@^3.0.1:
   version "3.0.1"
   resolved "https://registry.yarnpkg.com/scrypt-js/-/scrypt-js-3.0.1.tgz#d314a57c2aef69d1ad98a138a21fe9eafa9ee312"
@@ -11287,9 +11339,9 @@ semver@7.3.8:
     lru-cache "^6.0.0"
 
 semver@^6.0.0, semver@^6.1.1, semver@^6.1.2, semver@^6.3.0:
-  version "6.3.0"
-  resolved "https://registry.yarnpkg.com/semver/-/semver-6.3.0.tgz#ee0a64c8af5e8ceea67687b133761e1becbd1d3d"
-  integrity sha512-b39TBaTSfV6yBrapU89p5fKekE2m/NwnDocOVruQFS1/veMgdzuPcnOM34M6CwxW8jH/lxEa5rBoDeUwu5HHTw==
+  version "6.3.1"
+  resolved "https://registry.yarnpkg.com/semver/-/semver-6.3.1.tgz#556d2ef8689146e46dcea4bfdd095f3434dffcb4"
+  integrity sha512-BR7VvDCVHO+q2xBEWskxS6DJE1qRnb7DxzUrogb71CWoSficBxYsiAGd+Kl0mmq/MprG9yArRkyrQxTO6XjMzA==
 
 semver@^7.0.0, semver@^7.1.1, semver@^7.3.4, semver@^7.3.5, semver@^7.3.7:
   version "7.3.7"
@@ -11355,13 +11407,20 @@ send@0.19.0:
     range-parser "~1.2.1"
     statuses "2.0.1"
 
-serialize-javascript@6.0.0, serialize-javascript@^6.0.0:
+serialize-javascript@6.0.0:
   version "6.0.0"
   resolved "https://registry.yarnpkg.com/serialize-javascript/-/serialize-javascript-6.0.0.tgz#efae5d88f45d7924141da8b5c3a7a7e663fefeb8"
   integrity sha512-Qr3TosvguFt8ePWqsvRfrKyQXIiW+nGbYpy8XK24NQHE83caxWt+mIymTT19DGFbNWNLfEwsrkSmN64lVWB9ag==
   dependencies:
     randombytes "^2.1.0"
 
+serialize-javascript@^6.0.1:
+  version "6.0.2"
+  resolved "https://registry.yarnpkg.com/serialize-javascript/-/serialize-javascript-6.0.2.tgz#defa1e055c83bf6d59ea805d8da862254eb6a6c2"
+  integrity sha512-Saa1xPByTTq2gdeFZYLLo+RFE35NHZkAbqZeWNd3BpzppeVisAqpDjcp8dyf6uIvEqJRd46jemmyA4iFIeVk8g==
+  dependencies:
+    randombytes "^2.1.0"
+
 serve-static@1.16.0:
   version "1.16.0"
   resolved "https://registry.yarnpkg.com/serve-static/-/serve-static-1.16.0.tgz#2bf4ed49f8af311b519c46f272bf6ac3baf38a92"
@@ -11823,7 +11882,7 @@ string-length@^4.0.1:
     char-regex "^1.0.2"
     strip-ansi "^6.0.0"
 
-"string-width-cjs@npm:string-width@^4.2.0":
+"string-width-cjs@npm:string-width@^4.2.0", "string-width@^1.0.2 || 2 || 3 || 4", string-width@^4.1.0, string-width@^4.2.0, string-width@^4.2.3:
   version "4.2.3"
   resolved "https://registry.yarnpkg.com/string-width/-/string-width-4.2.3.tgz#269c7117d27b05ad2e536830a8ec895ef9c6d010"
   integrity sha512-wKyQRQpjJ0sIp62ErSZdGsjMJWsap5oRNihHhu6G7JVO/9jIB6UyevL+tXuOqrng8j/cxKTWyWUwvSTriiZz/g==
@@ -11841,15 +11900,6 @@ string-width@^1.0.1:
     is-fullwidth-code-point "^1.0.0"
     strip-ansi "^3.0.0"
 
-"string-width@^1.0.2 || 2 || 3 || 4", string-width@^4.1.0, string-width@^4.2.0, string-width@^4.2.3:
-  version "4.2.3"
-  resolved "https://registry.yarnpkg.com/string-width/-/string-width-4.2.3.tgz#269c7117d27b05ad2e536830a8ec895ef9c6d010"
-  integrity sha512-wKyQRQpjJ0sIp62ErSZdGsjMJWsap5oRNihHhu6G7JVO/9jIB6UyevL+tXuOqrng8j/cxKTWyWUwvSTriiZz/g==
-  dependencies:
-    emoji-regex "^8.0.0"
-    is-fullwidth-code-point "^3.0.0"
-    strip-ansi "^6.0.1"
-
 string-width@^5.0.1, string-width@^5.1.2:
   version "5.1.2"
   resolved "https://registry.yarnpkg.com/string-width/-/string-width-5.1.2.tgz#14f8daec6d81e7221d2a357e668cab73bdbca794"
@@ -11905,7 +11955,7 @@ string_decoder@~1.1.1:
   dependencies:
     safe-buffer "~5.1.0"
 
-"strip-ansi-cjs@npm:strip-ansi@^6.0.1":
+"strip-ansi-cjs@npm:strip-ansi@^6.0.1", strip-ansi@^6.0.0, strip-ansi@^6.0.1:
   version "6.0.1"
   resolved "https://registry.yarnpkg.com/strip-ansi/-/strip-ansi-6.0.1.tgz#9e26c63d30f53443e9489495b2105d37b67a85d9"
   integrity sha512-Y38VPSHcqkFrCpFnQ9vuSXmquuv5oXOKpGeT6aGrr3o3Gc9AlVa6JBfUSOCnbxGGZF+/0ooI7KrPuUSztUdU5A==
@@ -11919,13 +11969,6 @@ strip-ansi@^3.0.0, strip-ansi@^3.0.1:
   dependencies:
     ansi-regex "^2.0.0"
 
-strip-ansi@^6.0.0, strip-ansi@^6.0.1:
-  version "6.0.1"
-  resolved "https://registry.yarnpkg.com/strip-ansi/-/strip-ansi-6.0.1.tgz#9e26c63d30f53443e9489495b2105d37b67a85d9"
-  integrity sha512-Y38VPSHcqkFrCpFnQ9vuSXmquuv5oXOKpGeT6aGrr3o3Gc9AlVa6JBfUSOCnbxGGZF+/0ooI7KrPuUSztUdU5A==
-  dependencies:
-    ansi-regex "^5.0.1"
-
 strip-ansi@^7.0.1:
   version "7.0.1"
   resolved "https://registry.yarnpkg.com/strip-ansi/-/strip-ansi-7.0.1.tgz#61740a08ce36b61e50e65653f07060d000975fb2"
@@ -12043,7 +12086,7 @@ tar-stream@~2.2.0:
     inherits "^2.0.3"
     readable-stream "^3.1.1"
 
-tar@6.1.11, tar@^6.1.11, tar@^6.1.2:
+tar@6.1.11:
   version "6.1.11"
   resolved "https://registry.yarnpkg.com/tar/-/tar-6.1.11.tgz#6760a38f003afa1b2ffd0ffe9e9abbd0eab3d621"
   integrity sha512-an/KZQzQUkZCkuoAA64hM92X0Urb6VpRhAFllDzz44U2mcD5scmT3zBc4VgVpkugF580+DQn8eAFSyoQt0tznA==
@@ -12055,6 +12098,18 @@ tar@6.1.11, tar@^6.1.11, tar@^6.1.2:
     mkdirp "^1.0.3"
     yallist "^4.0.0"
 
+tar@^6.1.11, tar@^6.1.2:
+  version "6.2.1"
+  resolved "https://registry.yarnpkg.com/tar/-/tar-6.2.1.tgz#717549c541bc3c2af15751bea94b1dd068d4b03a"
+  integrity "sha1-cXVJxUG8PCrxV1G+qUsd0GjUsDo= sha512-DZ4yORTwrbTj/7MZYq2w+/ZFdI6OZ/f9SFHR+71gIVUZhOQPHzVCLpvRnPgyaMpfWxxk/4ONva3GQSyNIKRv6A=="
+  dependencies:
+    chownr "^2.0.0"
+    fs-minipass "^2.0.0"
+    minipass "^5.0.0"
+    minizlib "^2.1.1"
+    mkdirp "^1.0.3"
+    yallist "^4.0.0"
+
 temp-dir@1.0.0:
   version "1.0.0"
   resolved "https://registry.yarnpkg.com/temp-dir/-/temp-dir-1.0.0.tgz#0a7c0ea26d3a39afa7e0ebea9c1fc0bc4daa011d"
@@ -12076,24 +12131,24 @@ tempy@1.0.0:
     type-fest "^0.16.0"
     unique-string "^2.0.0"
 
-terser-webpack-plugin@^5.1.3:
-  version "5.3.5"
-  resolved "https://registry.yarnpkg.com/terser-webpack-plugin/-/terser-webpack-plugin-5.3.5.tgz#f7d82286031f915a4f8fb81af4bd35d2e3c011bc"
-  integrity sha512-AOEDLDxD2zylUGf/wxHxklEkOe2/r+seuyOWujejFrIxHf11brA1/dWQNIgXa1c6/Wkxgu7zvv0JhOWfc2ELEA==
+terser-webpack-plugin@^5.3.10:
+  version "5.3.10"
+  resolved "https://registry.yarnpkg.com/terser-webpack-plugin/-/terser-webpack-plugin-5.3.10.tgz#904f4c9193c6fd2a03f693a2150c62a92f40d199"
+  integrity sha512-BKFPWlPDndPs+NGGCr1U59t0XScL5317Y0UReNrHaw9/FwhPENlq6bfgs+4yPfyP51vqC1bQ4rp1EfXW5ZSH9w==
   dependencies:
-    "@jridgewell/trace-mapping" "^0.3.14"
+    "@jridgewell/trace-mapping" "^0.3.20"
     jest-worker "^27.4.5"
     schema-utils "^3.1.1"
-    serialize-javascript "^6.0.0"
-    terser "^5.14.1"
+    serialize-javascript "^6.0.1"
+    terser "^5.26.0"
 
-terser@^5.14.1:
-  version "5.14.2"
-  resolved "https://registry.yarnpkg.com/terser/-/terser-5.14.2.tgz#9ac9f22b06994d736174f4091aa368db896f1c10"
-  integrity sha512-oL0rGeM/WFQCUd0y2QrWxYnq7tfSuKBiqTjRPWrRgB46WD/kiwHwF8T23z78H6Q6kGCuuHcPB+KULHRdxvVGQA==
+terser@^5.26.0:
+  version "5.36.0"
+  resolved "https://registry.yarnpkg.com/terser/-/terser-5.36.0.tgz#8b0dbed459ac40ff7b4c9fd5a3a2029de105180e"
+  integrity sha512-IYV9eNMuFAV4THUspIRXkLakHnV6XO7FEdtKjf/mDyrnqUg9LnlOn6/RwRvM9SZjR4GUq8Nk8zj67FzVARr74w==
   dependencies:
-    "@jridgewell/source-map" "^0.3.2"
-    acorn "^8.5.0"
+    "@jridgewell/source-map" "^0.3.3"
+    acorn "^8.8.2"
     commander "^2.20.0"
     source-map-support "~0.5.20"
 
@@ -12607,6 +12662,14 @@ update-browserslist-db@^1.0.5:
     escalade "^3.1.1"
     picocolors "^1.0.0"
 
+update-browserslist-db@^1.1.1:
+  version "1.1.1"
+  resolved "https://registry.yarnpkg.com/update-browserslist-db/-/update-browserslist-db-1.1.1.tgz#80846fba1d79e82547fb661f8d141e0945755fe5"
+  integrity sha512-R8UzCaa9Az+38REPiJ1tXlImTJXlVfgHZsglwBD/k6nj76ctsH1E3q4doGrukiLQd3sGQYu56r5+lo5r94l29A==
+  dependencies:
+    escalade "^3.2.0"
+    picocolors "^1.1.0"
+
 uri-js@^4.2.2:
   version "4.4.1"
   resolved "https://registry.yarnpkg.com/uri-js/-/uri-js-4.4.1.tgz#9b1a52595225859e55f669d928f88c6c57f2a77e"
@@ -12785,10 +12848,10 @@ walker@^1.0.8:
   dependencies:
     makeerror "1.0.12"
 
-watchpack@^2.4.0:
-  version "2.4.0"
-  resolved "https://registry.yarnpkg.com/watchpack/-/watchpack-2.4.0.tgz#fa33032374962c78113f93c7f2fb4c54c9862a5d"
-  integrity sha512-Lcvm7MGST/4fup+ifyKi2hjyIAwcdI4HRgtvTpIUxBRhB+RFtUh8XtDOxUfctVCnhVi+QQj49i91OyvzkJl6cg==
+watchpack@^2.4.1:
+  version "2.4.2"
+  resolved "https://registry.yarnpkg.com/watchpack/-/watchpack-2.4.2.tgz#2feeaed67412e7c33184e5a79ca738fbd38564da"
+  integrity sha512-TnbFSbcOCcDgjZ4piURLCbJ3nJhznVh9kw6F6iokjiFPl8ONxe9A6nMDVXDiNbrSfLILs6vB07F7wLBrwPYzJw==
   dependencies:
     glob-to-regexp "^0.4.1"
     graceful-fs "^4.1.2"
@@ -12893,33 +12956,32 @@ webpack-sources@^3.2.3:
   integrity sha512-/DyMEOrDgLKKIG0fmvtz+4dUX/3Ghozwgm6iPp8KRhvn+eQf9+Q7GWxVNMk3+uCPWfdXYC4ExGBckIXdFEfH1w==
 
 webpack@^5, webpack@^5.73.0:
-  version "5.76.0"
-  resolved "https://registry.yarnpkg.com/webpack/-/webpack-5.76.0.tgz#f9fb9fb8c4a7dbdcd0d56a98e56b8a942ee2692c"
-  integrity sha512-l5sOdYBDunyf72HW8dF23rFtWq/7Zgvt/9ftMof71E/yUb1YLOBmTgA2K4vQthB3kotMrSj609txVE0dnr2fjA==
-  dependencies:
-    "@types/eslint-scope" "^3.7.3"
-    "@types/estree" "^0.0.51"
-    "@webassemblyjs/ast" "1.11.1"
-    "@webassemblyjs/wasm-edit" "1.11.1"
-    "@webassemblyjs/wasm-parser" "1.11.1"
-    acorn "^8.7.1"
-    acorn-import-assertions "^1.7.6"
-    browserslist "^4.14.5"
+  version "5.96.1"
+  resolved "https://registry.yarnpkg.com/webpack/-/webpack-5.96.1.tgz#3676d1626d8312b6b10d0c18cc049fba7ac01f0c"
+  integrity "sha1-NnbRYm2DEraxDQwYzASfunrAHww= sha512-l2LlBSvVZGhL4ZrPwyr8+37AunkcYj5qh8o6u2/2rzoPc8gxFJkLj1WxNgooi9pnoc06jh0BjuXnamM4qlujZA=="
+  dependencies:
+    "@types/eslint-scope" "^3.7.7"
+    "@types/estree" "^1.0.6"
+    "@webassemblyjs/ast" "^1.12.1"
+    "@webassemblyjs/wasm-edit" "^1.12.1"
+    "@webassemblyjs/wasm-parser" "^1.12.1"
+    acorn "^8.14.0"
+    browserslist "^4.24.0"
     chrome-trace-event "^1.0.2"
-    enhanced-resolve "^5.10.0"
-    es-module-lexer "^0.9.0"
+    enhanced-resolve "^5.17.1"
+    es-module-lexer "^1.2.1"
     eslint-scope "5.1.1"
     events "^3.2.0"
     glob-to-regexp "^0.4.1"
-    graceful-fs "^4.2.9"
+    graceful-fs "^4.2.11"
     json-parse-even-better-errors "^2.3.1"
     loader-runner "^4.2.0"
     mime-types "^2.1.27"
     neo-async "^2.6.2"
-    schema-utils "^3.1.0"
+    schema-utils "^3.2.0"
     tapable "^2.1.1"
-    terser-webpack-plugin "^5.1.3"
-    watchpack "^2.4.0"
+    terser-webpack-plugin "^5.3.10"
+    watchpack "^2.4.1"
     webpack-sources "^3.2.3"
 
 whatwg-encoding@^2.0.0:
@@ -13019,16 +13081,7 @@ workerpool@6.2.1:
   resolved "https://registry.yarnpkg.com/workerpool/-/workerpool-6.2.1.tgz#46fc150c17d826b86a008e5a4508656777e9c343"
   integrity sha512-ILEIE97kDZvF9Wb9f6h5aXK4swSlKGUcOEGiIYb2OOu/IrDU9iwj0fD//SsA6E5ibwJxpEvhullJY4Sl4GcpAw==
 
-"wrap-ansi-cjs@npm:wrap-ansi@^7.0.0":
-  version "7.0.0"
-  resolved "https://registry.yarnpkg.com/wrap-ansi/-/wrap-ansi-7.0.0.tgz#67e145cff510a6a6984bdf1152911d69d2eb9e43"
-  integrity sha512-YVGIj2kamLSTxw6NsZjoBxfSwsn0ycdesmc4p+Q21c5zPuZ1pl+NfxVdxPtdHvmNVOQ6XSYG4AUtyt/Fi7D16Q==
-  dependencies:
-    ansi-styles "^4.0.0"
-    string-width "^4.1.0"
-    strip-ansi "^6.0.0"
-
-wrap-ansi@^7.0.0:
+"wrap-ansi-cjs@npm:wrap-ansi@^7.0.0", wrap-ansi@^7.0.0:
   version "7.0.0"
   resolved "https://registry.yarnpkg.com/wrap-ansi/-/wrap-ansi-7.0.0.tgz#67e145cff510a6a6984bdf1152911d69d2eb9e43"
   integrity sha512-YVGIj2kamLSTxw6NsZjoBxfSwsn0ycdesmc4p+Q21c5zPuZ1pl+NfxVdxPtdHvmNVOQ6XSYG4AUtyt/Fi7D16Q==
```
