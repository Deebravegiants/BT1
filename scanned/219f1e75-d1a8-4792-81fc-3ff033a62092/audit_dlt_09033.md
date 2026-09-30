# [?] Address @daml/* security advisory (#14584)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-08-02
Source: https://github.com/digital-asset/daml/commit/4768d404b7302b39163ad1d46e2dc8872f8c3ff3
Type: security-commit

## Details
Address @daml/* security advisory (#14584)

- CVE-2022-25878

CHANGELOG_BEGIN
CHANGELOG_END

## Patch
### language-support/ts/packages/package.json
```diff
@@ -31,6 +31,7 @@
     "**/y18n": "^4.0.1",
     "**/@types/react-test-renderer": "^16.9.3 || ^17.0.0",
     "**/hosted-git-info": "^4.0.2",
+    "**/protobufjs": "^6.10.3",
     "**/string-width": "^4.2.3",
     "**/strip-ansi": "^6.0.1",
     "**/ansi-regex": "^5.0.1",
```

### language-support/ts/packages/yarn.lock
```diff
@@ -742,20 +742,20 @@
   resolved "https://registry.yarnpkg.com/@types/lodash/-/lodash-4.14.161.tgz#a21ca0777dabc6e4f44f3d07f37b765f54188b18"
   integrity sha512-EP6O3Jkr7bXvZZSZYlsgt5DIjiGr0dXP1/jVEwVLTFgg0d+3lWVQkRavYVQszV7dYUwvg0B8R0MBDpcmXg7XIA==
 
-"@types/long@^4.0.0":
-  version "4.0.1"
-  resolved "https://registry.yarnpkg.com/@types/long/-/long-4.0.1.tgz#459c65fa1867dafe6a8f322c4c51695663cc55e9"
-  integrity sha512-5tXH6Bx/kNGd3MgffdmP4dy2Z+G4eaXw0SE81Tq3BNadtnMR5/ySMzX4SLEzHJzSmPNn4HIdpQsBvXMUykr58w==
+"@types/long@^4.0.1":
+  version "4.0.2"
+  resolved "https://registry.yarnpkg.com/@types/long/-/long-4.0.2.tgz#b74129719fc8d11c01868010082d483b7545591a"
+  integrity sha512-MqTGEo5bj5t157U6fA/BiDynNkn0YknVdh48CMPkTSpFTVmvao5UQmm7uEF6xBEo7qIMAlY/JSleYaE6VOdpaA==
 
 "@types/node@*":
   version "16.11.6"
   resolved "https://registry.yarnpkg.com/@types/node/-/node-16.11.6.tgz#6bef7a2a0ad684cf6e90fcfe31cecabd9ce0a3ae"
   integrity sha512-ua7PgUoeQFjmWPcoo9khiPum3Pd60k4/2ZGXt18sm2Slk0W0xZTqt5Y0Ny1NyBiN1EVQ/+FaF9NcY4Qe6rwk5w==
 
-"@types/node@^10.1.0":
-  version "10.17.60"
-  resolved "https://registry.yarnpkg.com/@types/node/-/node-10.17.60.tgz#35f3d6213daed95da7f0f73e75bcc6980e90597b"
-  integrity sha512-F0KIgDJfy2nA3zMLmWGKxcH2ZVEtCZXHHdOQs2gSaQ27+lNeEfGxzkIw90aXswATX7AZ33tahPbzy6KAfUreVw==
+"@types/node@>=13.7.0":
+  version "18.6.3"
+  resolved "https://registry.yarnpkg.com/@types/node/-/node-18.6.3.tgz#4e4a95b6fe44014563ceb514b2598b3e623d1c98"
+  integrity sha512-6qKpDtoaYLM+5+AFChLhHermMQxc3TOEFIDzrZLPRGHPrLEwqFkkT5Kx3ju05g6X7uDPazz3jHbKPX0KzCjntg==
 
 "@types/prettier@^2.1.5":
   version "2.4.1"
@@ -2852,10 +2852,10 @@ prompts@^2.0.1:
     kleur "^3.0.3"
     sisteransi "^1.0.5"
 
-protobufjs@6.8.8:
-  version "6.8.8"
-  resolved "https://registry.yarnpkg.com/protobufjs/-/protobufjs-6.8.8.tgz#c8b4f1282fd7a90e6f5b109ed11c84af82908e7c"
-  integrity sha512-AAmHtD5pXgZfi7GMpllpO3q1Xw1OYldr+dMUlAnffGTAhqkg72WdmSY71uKBF/JuyiKs8psYbtKrhi0ASCD8qw==
+protobufjs@6.8.8, protobufjs@^6.10.3:
+  version "6.11.3"
+  resolved "https://registry.yarnpkg.com/protobufjs/-/protobufjs-6.11.3.tgz#637a527205a35caa4f3e2a9a4a13ddffe0e7af74"
+  integrity sha512-xL96WDdCZYdU7Slin569tFX712BxsxslWwAfAhCYjQKGTq7dAU91Lomy6nLLhh/dyGhk/YH4TwTSRxTzhuHyZg==
   dependencies:
     "@protobufjs/aspromise" "^1.1.2"
     "@protobufjs/base64" "^1.1.2"
@@ -2867,8 +2867,8 @@ protobufjs@6.8.8:
     "@protobufjs/path" "^1.1.2"
     "@protobufjs/pool" "^1.1.0"
     "@protobufjs/utf8" "^1.1.0"
-    "@types/long" "^4.0.0"
-    "@types/node" "^10.1.0"
+    "@types/long" "^4.0.1"
+    "@types/node" ">=13.7.0"
     long "^4.0.0"
 
 psl@^1.1.33:
```
