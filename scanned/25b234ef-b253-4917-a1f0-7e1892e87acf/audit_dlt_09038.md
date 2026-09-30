# [?] Address CVE-2022-0355 alert, resolve `simple-get` to 4.0.1 (#12655)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-01-30
Source: https://github.com/digital-asset/daml/commit/20836b16228d8ab70dcdf8b75cff6f2158d9a2b9
Type: security-commit

## Details
Address CVE-2022-0355 alert, resolve `simple-get` to 4.0.1 (#12655)

changelog_begin
changelog_end

## Patch
### compiler/daml-extension/package.json
```diff
@@ -154,6 +154,7 @@
         "vsce": "^2.6.3"
     },
     "resolutions": {
-        "**/markdown-it": "^12.3.2"
+        "**/markdown-it": "^12.3.2",
+        "**/simple-get": "^4.0.1"
     }
 }
```

### compiler/daml-extension/yarn.lock
```diff
@@ -246,12 +246,12 @@ css-what@^5.0.0, css-what@^5.0.1:
   resolved "https://registry.yarnpkg.com/css-what/-/css-what-5.0.1.tgz#3efa820131f4669a8ac2408f9c32e7c7de9f4cad"
   integrity sha512-FYDTSHb/7KXsWICVsxdmiExPjCfRC4qRFBdVwv7Ax9hMnvMmEjP9RfxTEZ3qPZGmADDn2vAKSo9UcN1jKVYscg==
 
-decompress-response@^4.2.0:
-  version "4.2.1"
-  resolved "https://registry.yarnpkg.com/decompress-response/-/decompress-response-4.2.1.tgz#414023cc7a302da25ce2ec82d0d5238ccafd8986"
-  integrity sha512-jOSne2qbyE+/r8G1VU+G/82LBs2Fs4LAsTiLSHOCOMZQl2OKZ6i8i4IyHemTe+/yIXOtTcRQMzPcgyhoFlqPkw==
+decompress-response@^6.0.0:
+  version "6.0.0"
+  resolved "https://registry.yarnpkg.com/decompress-response/-/decompress-response-6.0.0.tgz#ca387612ddb7e104bd16d85aab00d5ecf09c66fc"
+  integrity sha512-aW35yZM6Bb/4oJlZncMH2LCoZtJXTRxES17vE3hoRiowU2kWHaJKFkSBDnDR+cm9J+9QhXmREyIfv0pji9ejCQ==
   dependencies:
-    mimic-response "^2.0.0"
+    mimic-response "^3.1.0"
 
 deep-extend@^0.6.0:
   version "0.6.0"
@@ -534,7 +534,7 @@ lru-cache@^6.0.0:
   dependencies:
     yallist "^4.0.0"
 
-markdown-it@^10.0.0, markdown-it@^12.3.2:
+markdown-it@^12.3.2:
   version "12.3.2"
   resolved "https://registry.yarnpkg.com/markdown-it/-/markdown-it-12.3.2.tgz#bf92ac92283fe983fe4de8ff8abfb5ad72cd0c90"
   integrity sha512-TchMembfxfNVpHkbtriWltGWc+m3xszaRD0CZup7GFFhzIgQqxIfn3eGj1yZpfuflzPvfkt611B2Q/Bsk1YnGg==
@@ -567,10 +567,10 @@ mime@^1.3.4:
   resolved "https://registry.yarnpkg.com/mime/-/mime-1.6.0.tgz#32cd9e5c64553bd58d19a568af452acff04981b1"
   integrity sha512-x0Vn8spI+wuJ1O6S7gnbaQg8Pxh4NNHb7KSINmEWKiPE4RKOplvijn+NkmYmmRgP68mc70j2EbeTFRsrswaQeg==
 
-mimic-response@^2.0.0:
-  version "2.1.0"
-  resolved "https://registry.yarnpkg.com/mimic-response/-/mimic-response-2.1.0.tgz#d13763d35f613d09ec37ebb30bac0469c0ee8f43"
-  integrity sha512-wXqjST+SLt7R009ySCglWBCFpjUygmCIfD790/kVbiGmUgfYGuB14PiTd5DwVxSV4NcYHjzMkoj5LjQZwTQLEA==
+mimic-response@^3.1.0:
+  version "3.1.0"
+  resolved "https://registry.yarnpkg.com/mimic-response/-/mimic-response-3.1.0.tgz#2d1d59af9c1b129815accc2c46a022a5ce1fa3c9"
+  integrity sha512-z0yWI+4FDrrweS8Zmt4Ej5HdJmky15+L2e6Wgn3+iK5fWzb6T3fhNFq2+MeTRb064c6Wr4N/wv0DzQTjNzHNGQ==
 
 minimatch@^3.0.3, minimatch@^3.0.4:
   version "3.0.4"
@@ -827,12 +827,12 @@ simple-concat@^1.0.0:
   resolved "https://registry.yarnpkg.com/simple-concat/-/simple-concat-1.0.1.tgz#f46976082ba35c2263f1c8ab5edfe26c41c9552f"
   integrity sha512-cSFtAPtRhljv69IK0hTVZQ+OfE9nePi/rtJmw5UjHeVyVroEqJXP1sFztKUy1qU+xvz3u/sfYJLa947b7nAN2Q==
 
-simple-get@^3.0.3:
-  version "3.1.0"
-  resolved "https://registry.yarnpkg.com/simple-get/-/simple-get-3.1.0.tgz#b45be062435e50d159540b576202ceec40b9c6b3"
-  integrity sha512-bCR6cP+aTdScaQCnQKbPKtJOKDp/hj9EDLJo3Nw4y1QksqaovlW/bnptB6/c1e+qmNIDHRK+oXFDdEqBT8WzUA==
+simple-get@^3.0.3, simple-get@^4.0.1:
+  version "4.0.1"
+  resolved "https://registry.yarnpkg.com/simple-get/-/simple-get-4.0.1.tgz#4a39db549287c979d352112fa03fd99fd6bc3543"
+  integrity sha512-brv7p5WgH0jmQJr1ZDDfKDOSeWWg+OVypG99A/5vYGPqJ6pxiaHLy8nxtFjBA7oMa01ebA9gfh1uMCFqOuXxvA==
   dependencies:
-    decompress-response "^4.2.0"
+    decompress-response "^6.0.0"
     once "^1.3.1"
     simple-concat "^1.0.0"
 
@@ -986,9 +986,9 @@ util-deprecate@^1.0.1, util-deprecate@~1.0.1:
   integrity sha1-RQ1Nyfpw3nMnYvvS1KKJgUGaDM8=
 
 vsce@^2.6.3:
-  version "2.6.3"
-  resolved "https://registry.yarnpkg.com/vsce/-/vsce-2.6.3.tgz#5a50ec9894573350b10457064f71d1f2701789cf"
-  integrity sha512-PKfvAtG9rLT1evHiKOJpBHND1hUHOOf4lL7chZFp0KGu+Bpgcx3g3T5eq0d8Hmzd08zd3KJunsaA3iaNSmTU/A==
+  version "2.6.5"
+  resolved "https://registry.yarnpkg.com/vsce/-/vsce-2.6.5.tgz#74a0fad427bf7c25087746e6e16e1f7265f43361"
+  integrity sha512-KB3m0CDlWZCKwjQx2oSg35vWgTNrcOPcL6DGLVGewKhadwbL2OWGRoMRKUUFFtPFKwp3BwuTvEM5fENG/AQ5Lg==
   dependencies:
     azure-devops-node-api "^11.0.1"
     chalk "^2.4.2"
@@ -998,7 +998,7 @@ vsce@^2.6.3:
     hosted-git-info "^4.0.2"
     keytar "^7.7.0"
     leven "^3.1.0"
-    markdown-it "^10.0.0"
+    markdown-it "^12.3.2"
     mime "^1.3.4"
     minimatch "^3.0.3"
     parse-semver "^1.1.1"
```
