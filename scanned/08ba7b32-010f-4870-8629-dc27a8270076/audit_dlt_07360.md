# [?] Fix reported vulnerabilities (#12443)

## Summary
Severity: Unknown
Chain: Canton/Daml
Component: digital-asset/daml
Published: 2022-01-17
Source: https://github.com/digital-asset/daml/commit/69a8b6797e5424420d6dca32989d035a211ec69c
Type: security-commit

## Details
Fix reported vulnerabilities (#12443)

changelog_begin
changelog_end

Bump resolved markdown-it version to 12.3.2 for modernizr

Bump webpack-dev-server to 4.3.7 to fix transitive issue reported on selfsigned 1.x

Bump marked to 4.0.10 to address reported vulnerability

## Patch
### language-support/ts/packages/package.json
```diff
@@ -29,6 +29,7 @@
   },
   "resolutions": {
     "marked": "^2.0.0",
+    "typedoc/**/marked": "^4.0.10",
     "**/y18n": "^4.0.1",
     "**/@types/react-test-renderer": "^16.9.3 || ^17.0.0",
     "**/hosted-git-info": "^4.0.2",
```

### language-support/ts/packages/yarn.lock
```diff
@@ -2535,6 +2535,11 @@ marked@^1.1.1, marked@^2.0.0:
   resolved "https://registry.yarnpkg.com/marked/-/marked-2.1.3.tgz#bd017cef6431724fd4b27e0657f5ceb14bff3753"
   integrity sha512-/Q+7MGzaETqifOMWYEA7HVMaZb4XbcRfaOzcSsHZEith83KGlvaSG33u0SKu89Mj5h+T8V2hM+8O45Qc5XTgwA==
 
+marked@^4.0.10:
+  version "4.0.10"
+  resolved "https://registry.yarnpkg.com/marked/-/marked-4.0.10.tgz#423e295385cc0c3a70fa495e0df68b007b879423"
+  integrity sha512-+QvuFj0nGgO970fySghXGmuw+Fd0gD2x3+MqCWLIPf5oxdv1Ka6b2q+z9RP01P/IaKPMEramy+7cNy/Lw8c3hw==
+
 merge-stream@^2.0.0:
   version "2.0.0"
   resolved "https://registry.yarnpkg.com/merge-stream/-/merge-stream-2.0.0.tgz#52823629a14dd00c9770fb6ad47dc6310f2c1f60"
```

### navigator/frontend/package.json
```diff
@@ -58,7 +58,7 @@
     "val-loader": "^4.0.0",
     "webpack": "^5.54.0",
     "webpack-cli": "^4.8.0",
-    "webpack-dev-server": "^4.3.0"
+    "webpack-dev-server": "^4.7.3"
   },
   "dependencies": {
     "@apollo/client": "^3.3.2",
@@ -99,6 +99,7 @@
     "**/css-what": "^5.0.1",
     "**/glob-parent": "^6.0.0",
     "**/set-value": "^4.0.1",
-    "html-webpack-plugin/**/strip-ansi": "^6.0.0"
+    "html-webpack-plugin/**/strip-ansi": "^6.0.0",
+    "modernizr/**/markdown-it": "^12.3.2"
   }
 }
```

### navigator/frontend/yarn.lock
```diff
@@ -274,6 +274,21 @@
   dependencies:
     "@types/babel-types" "*"
 
+"@types/body-parser@*":
+  version "1.19.2"
+  resolved "https://registry.yarnpkg.com/@types/body-parser/-/body-parser-1.19.2.tgz#aea2059e28b7658639081347ac4fab3de166e6f0"
+  integrity sha512-ALYone6pm6QmwZoAgeyNksccT9Q4AWZQ6PvfwR37GT6r6FWUPguq6sUmNGSMV2Wr761oQoBxwGGa6DR5o1DC9g==
+  dependencies:
+    "@types/connect" "*"
+    "@types/node" "*"
+
+"@types/bonjour@^3.5.9":
+  version "3.5.10"
+  resolved "https://registry.yarnpkg.com/@types/bonjour/-/bonjour-3.5.10.tgz#0f6aadfe00ea414edc86f5d106357cda9701e275"
+  integrity sha512-p7ienRMiS41Nu2/igbJxxLDWrSZ0WxM8UQgCeO9KhoVF7cOVFkrKsiDr1EsJIla8vV3oEEjGcz11jc5yimhzZw==
+  dependencies:
+    "@types/node" "*"
+
 "@types/classnames@^2.2.11":
   version "2.3.1"
   resolved "https://registry.yarnpkg.com/@types/classnames/-/classnames-2.3.1.tgz#3c2467aa0f1a93f1f021e3b9bcf938bd5dfdc0dd"
@@ -300,6 +315,21 @@
   dependencies:
     "@types/color-convert" "*"
 
+"@types/connect-history-api-fallback@^1.3.5":
+  version "1.3.5"
+  resolved "https://registry.yarnpkg.com/@types/connect-history-api-fallback/-/connect-history-api-fallback-1.3.5.tgz#d1f7a8a09d0ed5a57aee5ae9c18ab9b803205dae"
+  integrity sha512-h8QJa8xSb1WD4fpKBDcATDNGXghFj6/3GRWG6dhmRcu0RX1Ubasur2Uvx5aeEwlf0MwblEC2bMzzMQntxnw/Cw==
+  dependencies:
+    "@types/express-serve-static-core" "*"
+    "@types/node" "*"
+
+"@types/connect@*":
+  version "3.4.35"
+  resolved "https://registry.yarnpkg.com/@types/connect/-/connect-3.4.35.tgz#5fcf6ae445e4021d1fc2219a4873cc73a3bb2ad1"
+  integrity sha512-cdeYyv4KWoEgpBISTxWvqYsVy444DOqehiF3fM3ne10AmJ62RSyNkUnxMJXHQWRQQX2eR94m5y1IZyDwBjV9FQ==
+  dependencies:
+    "@types/node" "*"
+
 "@types/deep-equal@^1.0.1":
   version "1.0.1"
   resolved "https://registry.yarnpkg.com/@types/deep-equal/-/deep-equal-1.0.1.tgz#71cfabb247c22bcc16d536111f50c0ed12476b03"
@@ -339,6 +369,25 @@
   resolved "https://registry.yarnpkg.com/@types/estree/-/estree-0.0.50.tgz#1e0caa9364d3fccd2931c3ed96fdbeaa5d4cca83"
   integrity sha512-C6N5s2ZFtuZRj54k2/zyRhNDjJwwcViAM3Nbm8zjBpbqAdZ00mr0CFxvSKeO8Y/e03WVFLpQMdHYVfUd6SB+Hw==
 
+"@types/express-serve-static-core@*", "@types/express-serve-static-core@^4.17.18":
+  version "4.17.28"
+  resolved "https://registry.yarnpkg.com/@types/express-serve-static-core/-/express-serve-static-core-4.17.28.tgz#c47def9f34ec81dc6328d0b1b5303d1ec98d86b8"
+  integrity sha512-P1BJAEAW3E2DJUlkgq4tOL3RyMunoWXqbSCygWo5ZIWTjUgN1YnaXWW4VWl/oc8vs/XoYibEGBKP0uZyF4AHig==
+  dependencies:
+    "@types/node" "*"
+    "@types/qs" "*"
+    "@types/range-parser" "*"
+
+"@types/express@*":
+  version "4.17.13"
+  resolved "https://registry.yarnpkg.com/@types/express/-/express-4.17.13.tgz#a76e2995728999bab51a33fabce1d705a3709034"
+  integrity sha512-6bSZTPaTIACxn48l50SR+axgrqm6qXFIxrdAKaG6PaJk3+zuUr35hBlgT7vOmJcum+OEaIBLtHV/qloEAFITeA==
+  dependencies:
+    "@types/body-parser" "*"
+    "@types/express-serve-static-core" "^4.17.18"
+    "@types/qs" "*"
+    "@types/serve-static" "*"
+
 "@types/hoist-non-react-statics@*", "@types/hoist-non-react-statics@^3.3.0":
   version "3.3.1"
   resolved "https://registry.yarnpkg.com/@types/hoist-non-react-statics/-/hoist-non-react-statics-3.3.1.tgz#1124aafe5118cb591977aeb1ceaaed1070eb039f"
@@ -364,7 +413,7 @@
   resolved "https://registry.yarnpkg.com/@types/json-schema/-/json-schema-7.0.7.tgz#98a993516c859eb0d5c4c8f098317a9ea68db9ad"
   integrity sha512-cxWFQVseBm6O9Gbw1IWb8r6OS4OhSt3hPZLkFApLjM8TEXROBuQGLAH2i2gZpcXdLBIrpXuTDhH7Vbm1iXmNGA==
 
-"@types/json-schema@^7.0.8":
+"@types/json-schema@^7.0.8", "@types/json-schema@^7.0.9":
   version "7.0.9"
   resolved "https://registry.yarnpkg.com/@types/json-schema/-/json-schema-7.0.9.tgz#97edc9037ea0c38585320b28964dde3b39e4660d"
   integrity sha512-qcUXuemtEu+E5wZSJHNxUXeCZhAfXKQ41D+duX+VYPde7xyEVZci+/oXKJL13tnRs9lR2pr4fod59GT6/X1/yQ==
@@ -386,6 +435,11 @@
   dependencies:
     "@types/unist" "*"
 
+"@types/mime@^1":
+  version "1.3.2"
+  resolved "https://registry.yarnpkg.com/@types/mime/-/mime-1.3.2.tgz#93e25bf9ee75fe0fd80b594bc4feb0e862111b5a"
+  integrity sha512-YATxVxgRqNH6nHEIsvg6k2Boc1JHI9ZbH5iWFFv/MTkchz3b1ieGDa5T0a9RznNdI0KhVbdbWSN+KWWrQZRxTw==
+
 "@types/modernizr@^3.5.3":
   version "3.5.3"
   resolved "https://registry.yarnpkg.com/@types/modernizr/-/modernizr-3.5.3.tgz#8ef99e6252191c1d88647809109dc29884ba6d7a"
@@ -401,6 +455,16 @@
   resolved "https://registry.yarnpkg.com/@types/prop-types/-/prop-types-15.7.3.tgz#2ab0d5da2e5815f94b0b9d4b95d1e5f243ab2ca7"
   integrity sha512-KfRL3PuHmqQLOG+2tGpRO26Ctg+Cq1E01D2DMriKEATHgWLfeNDmq9e29Q9WIky0dQ3NPkd1mzYH8Lm936Z9qw==
 
+"@types/qs@*":
+  version "6.9.7"
+  resolved "https://registry.yarnpkg.com/@types/qs/-/qs-6.9.7.tgz#63bb7d067db107cc1e457c303bc25d511febf6cb"
+  integrity sha512-FGa1F62FT09qcrueBA6qYTrJPVDzah9a+493+o2PCXsesWHIn27G98TsSMs3WPNbZIEj4+VJf6saSFpvD+3Zsw==
+
+"@types/range-parser@*":
+  version "1.2.4"
+  resolved "https://registry.yarnpkg.com/@types/range-parser/-/range-parser-1.2.4.tgz#cd667bcfdd025213aafb7ca5915a932590acdcdc"
+  integrity sha512-EEhsLsD6UsDM1yFhAvy0Cjr6VwmpMWqFBCb9w07wVugF7w9nfajxLuVmngTIpgS6svCnm6Vaw+MZhoDCKnOfsw==
+
 "@types/react-autosuggest@^10.0.1":
   version "10.1.4"
   resolved "https://registry.yarnpkg.com/@types/react-autosuggest/-/react-autosuggest-10.1.4.tgz#9e16bf03f68d4fcf98f506e84acb9f200cd3022b"
@@ -464,6 +528,28 @@
   resolved "https://registry.yarnpkg.com/@types/scheduler/-/scheduler-0.16.1.tgz#18845205e86ff0038517aab7a18a62a6b9f71275"
   integrity sha512-EaCxbanVeyxDRTQBkdLb3Bvl/HK7PBK6UJjsSixB0iHKoWxE5uu2Q/DgtpOhPIojN0Zl1whvOd7PoHs2P0s5eA==
 
+"@types/serve-index@^1.9.1":
+  version "1.9.1"
+  resolved "https://registry.yarnpkg.com/@types/serve-index/-/serve-index-1.9.1.tgz#1b5e85370a192c01ec6cec4735cf2917337a6278"
+  integrity sha512-d/Hs3nWDxNL2xAczmOVZNj92YZCS6RGxfBPjKzuu/XirCgXdpKEb88dYNbrYGint6IVWLNP+yonwVAuRC0T2Dg==
+  dependencies:
+    "@types/express" "*"
+
+"@types/serve-static@*":
+  version "1.13.10"
+  resolved "https://registry.yarnpkg.com/@types/serve-static/-/serve-static-1.13.10.tgz#f5e0ce8797d2d7cc5ebeda48a52c96c4fa47a8d9"
+  integrity sha512-nCkHGI4w7ZgAdNkrEu0bv+4xNV/XDqW+DydknebMOQwkpDGx8G+HTlj7R7ABI8i8nKxVw0wtKPi1D+lPOkh4YQ==
+  dependencies:
+    "@types/mime" "^1"
+    "@types/node" "*"
+
+"@types/sockjs@^0.3.33":
+  version "0.3.33"
+  resolved "https://registry.yarnpkg.com/@types/sockjs/-/sockjs-0.3.33.tgz#570d3a0b99ac995360e3136fd6045113b1bd236f"
+  integrity sha512-f0KEEe05NvUnat+boPTZ0dgaLZ4SfSouXUgv5noUiefG2ajgKjmETo9ZJyuqsl7dfl2aHlLJUiki6B4ZYldiiw==
+  dependencies:
+    "@types/node" "*"
+
 "@types/styled-components@^5.1.0":
   version "5.1.9"
   resolved "https://registry.yarnpkg.com/@types/styled-components/-/styled-components-5.1.9.tgz#00d3d84b501420521c4db727e3c195459f87a6cf"
@@ -483,6 +569,13 @@
   resolved "https://registry.yarnpkg.com/@types/warning/-/warning-3.0.0.tgz#0d2501268ad8f9962b740d387c4654f5f8e23e52"
   integrity sha1-DSUBJorY+ZYrdA04fEZU9fjiPlI=
 
+"@types/ws@^8.2.2":
+  version "8.2.2"
+  resolved "https://registry.yarnpkg.com/@types/ws/-/ws-8.2.2.tgz#7c5be4decb19500ae6b3d563043cd407bf366c21"
+  integrity sha512-NOn5eIcgWLOo6qW8AcuLZ7G8PycXu0xTxxkS6Q18VWFxgPUSOwV0pBj2a/4viNZVu25i7RIB7GttdkAIUUXOOg==
+  dependencies:
+    "@types/node" "*"
+
 "@types/zen-observable@^0.8.0":
   version "0.8.2"
   resolved "https://registry.yarnpkg.com/@types/zen-observable/-/zen-observable-0.8.2.tgz#808c9fa7e4517274ed555fa158f2de4b4f468e71"
@@ -768,11 +861,25 @@ aggregate-error@^3.0.0:
     clean-stack "^2.0.0"
     indent-string "^4.0.0"
 
+ajv-formats@^2.1.1:
+  version "2.1.1"
+  resolved "https://registry.yarnpkg.com/ajv-formats/-/ajv-formats-2.1.1.tgz#6e669400659eb74973bbf2e33327180a0996b520"
+  integrity sha512-Wx0Kx52hxE7C18hkMEggYlEifqWZtYaRgouJor+WMdPnQyEK13vgEWyVNup7SoeeoLMsr4kf5h6dOW11I15MUA==
+  dependencies:
+    ajv "^8.0.0"
+
 ajv-keywords@^3.5.2:
   version "3.5.2"
   resolved "https://registry.yarnpkg.com/ajv-keywords/-/ajv-keywords-3.5.2.tgz#31f29da5ab6e00d1c2d329acf7b5929614d5014d"
   integrity sha512-5p6WTN0DdTGVQk6VjcEju19IgaHudalcfabD7yhDGeA6bcQnmL+CpveLJq/3hvfwd1aof6L386Ougkx6RfyMIQ==
 
+ajv-keywords@^5.0.0:
+  version "5.1.0"
+  resolved "https://registry.yarnpkg.com/ajv-keywords/-/ajv-keywords-5.1.0.tgz#69d4d385a4733cdbeab44964a1170a88f87f0e16"
+  integrity sha512-YCS/JNFAUyr5vAuhk1DWm1CBxRHW9LbJ2ozWeemrIqpbsqKjHVxYPyi5GC0rjZIT5JxJ3virVTS8wk4i/Z+krw==
+  dependencies:
+    fast-deep-equal "^3.1.3"
+
 ajv@^6.10.0, ajv@^6.12.4, ajv@^6.12.5:
   version "6.12.6"
   resolved "https://registry.yarnpkg.com/ajv/-/ajv-6.12.6.tgz#baf5a62e802b07d977034586f8c3baf5adf26df4"
@@ -783,6 +890,16 @@ ajv@^6.10.0, ajv@^6.12.4, ajv@^6.12.5:
     json-schema-traverse "^0.4.1"
     uri-js "^4.2.2"
 
+ajv@^8.0.0, ajv@^8.8.0:
+  version "8.9.0"
+  resolved "https://registry.yarnpkg.com/ajv/-/ajv-8.9.0.tgz#738019146638824dea25edcf299dcba1b0e7eb18"
+  integrity sha512-qOKJyNj/h+OWx7s5DePL6Zu1KeM9jPZhwBqs+7DzP6bGOvqzVCSf0xueYmVuaC/oQ/VtS2zLMLHdQFbkka+XDQ==
+  dependencies:
+    fast-deep-equal "^3.1.1"
+    json-schema-traverse "^1.0.0"
+    require-from-string "^2.0.2"
+    uri-js "^4.2.2"
+
 ajv@^8.0.1:
   version "8.2.0"
   resolved "https://registry.yarnpkg.com/ajv/-/ajv-8.2.0.tgz#c89d3380a784ce81b2085f48811c4c101df4c602"
@@ -842,6 +959,11 @@ argparse@^1.0.7:
   dependencies:
     sprintf-js "~1.0.2"
 
+argparse@^2.0.1:
+  version "2.0.1"
+  resolved "https://registry.yarnpkg.com/argparse/-/argparse-2.0.1.tgz#246f50f3ca78a3240f6c997e8a9bd1eac49e4b38"
+  integrity sha512-8+9WqebbFzpX9OR+Wa6O29asIogeRMzcGtAINdpMHHyAg10f05aSFVBbcEqGf/PXw1EjAZ+q2/bEBg3DvurK3Q==
+
 array-filter@^1.0.0:
   version "1.0.0"
   resolved "https://registry.yarnpkg.com/array-filter/-/array-filter-1.0.0.tgz#baf79e62e6ef4c2a4c0b831232daffec251f9d83"
@@ -1164,7 +1286,7 @@ cheerio@^1.0.0-rc.3:
     parse5-htmlparser2-tree-adapter "^6.0.1"
     tslib "^2.2.0"
 
-chokidar@^3.5.1:
+chokidar@^3.5.2:
   version "3.5.2"
   resolved "https://registry.yarnpkg.com/chokidar/-/chokidar-3.5.2.tgz#dba3976fcadb016f66fd365021d91600d01c1e75"
   integrity sha512-ekGhOnNVPgT77r4K/U3GDhu+FQ2S8TnK/s2KbIGXi0SZWuwkZ2QNyfWdZW+TVfn84DpEP7rLeCt2UI6bJ8GwbQ==
@@ -1502,7 +1624,7 @@ deep-is@^0.1.3:
   resolved "https://registry.yarnpkg.com/deep-is/-/deep-is-0.1.3.tgz#b369d6fb5dbc13eecf524f91b070feedc357cf34"
   integrity sha1-s2nW+128E+7PUk+RsHD+7cNXzzQ=
 
-default-gateway@^6.0.0:
+default-gateway@^6.0.3:
   version "6.0.3"
   resolved "https://registry.yarnpkg.com/default-gateway/-/default-gateway-6.0.3.tgz#819494c888053bdb743edbf343d6cdf7f2943a71"
   integrity sha512-fwSOJsbbNzZ/CUFpqFBqYfYNLj1NbMPm8MMCIzHjC83iSJRBEGmDUxU+WP661BaBQImeC2yHwXtz+P/O9o+XEg==
@@ -1738,10 +1860,10 @@ entities@^2.0.0:
   resolved "https://registry.yarnpkg.com/entities/-/entities-2.2.0.tgz#098dc90ebb83d8dffa089d55256b351d34c4da55"
   integrity sha512-p92if5Nz619I0w+akJrLZH0MX0Pb5DX39XOwQTtXSdQQOaYH03S1uIQp4mhOZtAXrxq4ViO67YTiLBo2638o9A==
 
-entities@~2.0.0:
-  version "2.0.3"
-  resolved "https://registry.yarnpkg.com/entities/-/entities-2.0.3.tgz#5c487e5742ab93c15abb5da22759b8590ec03b7f"
-  integrity sha512-MyoZ0jgnLvB2X3Lg5HqpFmn1kybDiIfEQmKzTb5apr51Rb+T3KdmMiqa70T+bhGnyv7bQ6WMj2QMHpGMmlrUYQ==
+entities@~2.1.0:
+  version "2.1.0"
+  resolved "https://registry.yarnpkg.com/entities/-/entities-2.1.0.tgz#992d3129cf7df6870b96c57858c249a120f8b8b5"
+  integrity sha512-hCx1oky9PFrJ611mf0ifBLBRW8lUUVRlFolb5gWRfIELabBlbp9xZvrqZLZAs+NxFnbfQoeGd8wDkygjg7U85w==
 
 envinfo@^7.7.3:
   version "7.8.1"
@@ -2121,7 +2243,7 @@ extend@^3.0.0:
   resolved "https://registry.yarnpkg.com/extend/-/extend-3.0.2.tgz#f8b1136b4071fbd8eb140aff858b1019ec2915fa"
   integrity sha512-fjquC59cD7CyW6urNXK0FBufkZcoiGG80wTuPujX590cB5Ttln20E2UB4S/WARVqhXffZl2LNgS+gQdPIIim/g==
 
-fast-deep-equal@^3.1.1:
+fast-deep-equal@^3.1.1, fast-deep-equal@^3.1.3:
   version "3.1.3"
   resolved "https://registry.yarnpkg.com/fast-deep-equal/-/fast-deep-equal-3.1.3.tgz#3a7d56b559d6cbc3eb512325244e619a65c6c525"
   integrity sha512-f3qQ9oQy9j2AhBe/H9VC91wLmKBCCU/gDOnKNAYG5hswO7BLKj09Hc5HYNz9cGI++xlpDCIgDaitVs03ATR84Q==
@@ -2669,16 +2791,6 @@ inherits@2.0.3:
   resolved "https://registry.yarnpkg.com/inherits/-/inherits-2.0.3.tgz#633c2c83e3da42a502f52466022480f4208261de"
   integrity sha1-Yzwsg+PaQqUC9SRmAiSA9CCCYd4=
 
-internal-ip@^6.2.0:
-  version "6.2.0"
-  resolved "https://registry.yarnpkg.com/internal-ip/-/internal-ip-6.2.0.tgz#d5541e79716e406b74ac6b07b856ef18dc1621c1"
-  integrity sha512-D8WGsR6yDt8uq7vDMu7mjcR+yRMm3dW8yufyChmszWRjcSHuxLBkR3GdS2HZAjodsaGuCvXeEJpueisXJULghg==
-  dependencies:
-    default-gateway "^6.0.0"
-    ipaddr.js "^1.9.1"
-    is-ip "^3.1.0"
-    p-event "^4.2.0"
-
 internal-slot@^1.0.3:
   version "1.0.3"
   resolved "https://registry.yarnpkg.com/internal-slot/-/internal-slot-1.0.3.tgz#7347e307deeea2faac2ac6205d4bc7d34967f59c"
@@ -2700,17 +2812,12 @@ invariant@^2.2.4:
   dependencies:
     loose-envify "^1.0.0"
 
-ip-regex@^4.0.0:
-  version "4.3.0"
-  resolved "https://registry.yarnpkg.com/ip-regex/-/ip-regex-4.3.0.tgz#687275ab0f57fa76978ff8f4dddc8a23d5990db5"
-  integrity sha512-B9ZWJxHHOHUhUjCPrMpLD4xEq35bUTClHM1S6CBU5ixQnkZmwipwgc96vAd7AAGM9TGHvJR+Uss+/Ak6UphK+Q==
-
 ip@^1.1.0:
   version "1.1.5"
   resolved "https://registry.yarnpkg.com/ip/-/ip-1.1.5.tgz#bdded70114290828c0a039e72ef25f5aaec4354a"
   integrity sha1-vd7XARQpCCjAoDnnLvJfWq7ENUo=
 
-ipaddr.js@1.9.1, ipaddr.js@^1.9.1:
+ipaddr.js@1.9.1:
   version "1.9.1"
   resolved "https://registry.yarnpkg.com/ipaddr.js/-/ipaddr.js-1.9.1.tgz#bff38543eeb8984825079ff3a2a8e6cbd46781b3"
   integrity sha512-0KI/607xoxSToH7GjN1FfSbLoU0+btTicjsQSWQlh/hZykN8KpmMf7uYwPW3R+akZ6R/w18ZlXSHBYXiYUPO3g==
@@ -2823,13 +2930,6 @@ is-hexadecimal@^1.0.0:
   resolved "https://registry.yarnpkg.com/is-hexadecimal/-/is-hexadecimal-1.0.4.tgz#cc35c97588da4bd49a8eedd6bc4082d44dcb23a7"
   integrity sha512-gyPJuv83bHMpocVYoqof5VDiZveEoGoFL8m3BXNb2VW8Xs+rz9kqO8LOQ5DH6EsuvilT1ApazU0pyl+ytbPtlw==
 
-is-ip@^3.1.0:
-  version "3.1.0"
-  resolved "https://registry.yarnpkg.com/is-ip/-/is-ip-3.1.0.tgz#2ae5ddfafaf05cb8008a62093cf29734f657c5d8"
-  integrity sha512-35vd5necO7IitFPjd/YBeqwWnyDWbuLH9ZXQdMfDA8TEo7pv5X8yfrvVO3xbJbLUlERCMvf6X0hTUamQxCYJ9Q==
-  dependencies:
-    ip-regex "^4.0.0"
-
 is-map@^2.0.1, is-map@^2.0.2:
   version "2.0.2"
   resolved "https://registry.yarnpkg.com/is-map/-/is-map-2.0.2.tgz#00922db8c9bf73e81b7a335827bc2a43f2b91127"
@@ -3092,10 +3192,10 @@ license-checker@^25.0.1:
     spdx-satisfies "^4.0.0"
     treeify "^1.1.0"
 
-linkify-it@^2.0.0:
-  version "2.2.0"
-  resolved "https://registry.yarnpkg.com/linkify-it/-/linkify-it-2.2.0.tgz#e3b54697e78bf915c70a38acd78fd09e0058b1cf"
-  integrity sha512-GnAl/knGn+i1U/wjBz3akz2stz+HrHLsxMwHQGofCDfPvlf+gDKN58UtfmUquTY4/MXeE2x7k19KQmeoZi94Iw==
+linkify-it@^3.0.1:
+  version "3.0.3"
+  resolved "https://registry.yarnpkg.com/linkify-it/-/linkify-it-3.0.3.tgz#a98baf44ce45a550efb4d49c769d07524cc2fa2e"
+  integrity sha512-ynTsyrFSdE5oZ/O9GEf00kPngmOfVwazR5GKDq6EYfhlpFug3J2zybX56a2PRRpc9P+FuSoGNAwjlbDs9jJBPQ==
   dependencies:
     uc.micro "^1.0.1"
 
@@ -3199,14 +3299,14 @@ lru-cache@^6.0.0:
   dependencies:
     yallist "^4.0.0"
 
-markdown-it@^10.0.0:
-  version "10.0.0"
-  resolved "https://registry.yarnpkg.com/markdown-it/-/markdown-it-10.0.0.tgz#abfc64f141b1722d663402044e43927f1f50a8dc"
-  integrity sha512-YWOP1j7UbDNz+TumYP1kpwnP0aEa711cJjrAQrzd0UXlbJfc5aAq0F/PZHjiioqDC1NKgvIMX+o+9Bk7yuM2dg==
+markdown-it@^10.0.0, markdown-it@^12.3.2:
+  version "12.3.2"
+  resolved "https://registry.yarnpkg.com/markdown-it/-/markdown-it-12.3.2.tgz#bf92ac92283fe983fe4de8ff8abfb5ad72cd0c90"
+  integrity sha512-TchMembfxfNVpHkbtriWltGWc+m3xszaRD0CZup7GFFhzIgQqxIfn3eGj1yZpfuflzPvfkt611B2Q/Bsk1YnGg==
   dependencies:
-    argparse "^1.0.7"
-    entities "~2.0.0"
-    linkify-it "^2.0.0"
+    argparse "^2.0.1"
+    entities "~2.1.0"
+    linkify-it "^3.0.1"
     mdurl "^1.0.1"
     uc.micro "^1.0.5"
 
@@ -3658,18 +3758,6 @@ osenv@^0.1.4:
     os-homedir "^1.0.0"
     os-tmpdir "^1.0.0"
 
-p-event@^4.2.0:
-  version "4.2.0"
-  resolved "https://registry.yarnpkg.com/p-event/-/p-event-4.2.0.tgz#af4b049c8acd91ae81083ebd1e6f5cae2044c1b5"
-  integrity sha512-KXatOjCRXXkSePPb1Nbi0p0m+gQAwdlbhi4wQKJPI1HsMQS9g+Sqp2o+QHziPr7eYJyOZet836KoHEVM1mwOrQ==
-  dependencies:
-    p-timeout "^3.1.0"
-
-p-finally@^1.0.0:
-  version "1.0.0"
-  resolved "https://registry.yarnpkg.com/p-finally/-/p-finally-1.0.0.tgz#3fbcfb15b899a44123b34b6dcc18b724336a2cae"
-  integrity sha1-P7z7FbiZpEEjs0ttzBi3JDNqLK4=
-
 p-limit@^1.1.0:
   version "1.3.0"
   resolved "https://registry.yarnpkg.com/p-limit/-/p-limit-1.3.0.tgz#b86bd5f0c25690911c7590fcbfc2010d54b3ccb8"
@@ -3720,13 +3808,6 @@ p-retry@^4.5.0:
     "@types/retry" "^0.12.0"
     retry "^0.13.1"
 
-p-timeout@^3.1.0:
-  version "3.2.0"
-  resolved "https://registry.yarnpkg.com/p-timeout/-/p-timeout-3.2.0.tgz#c7e17abc971d2a7962ef83626b35d635acf23dfe"
-  integrity sha512-rhIwUycgwwKcP9yTOOFK/AKsAopjjCakVqLHePO3CC6Mir1Z99xT+R63jZxAT5lFZLa2inS5h+ZS2GvR99/FBg==
-  dependencies:
-    p-finally "^1.0.0"
-
 p-try@^1.0.0:
   version "1.0.0"
   resolved "https://registry.yarnpkg.com/p-try/-/p-try-1.0.0.tgz#cbc79cdbaf8fd4228e13f621f2b1a237c1b207b3"
@@ -3966,11 +4047,6 @@ proxy-addr@~2.0.5:
     forwarded "~0.1.2"
     ipaddr.js "1.9.1"
 
-punycode@1.3.2:
-  version "1.3.2"
-  resolved "https://registry.yarnpkg.com/punycode/-/punycode-1.3.2.tgz#9653a036fb7c1ee42342f2325cceefea3926c48d"
-  integrity sha1-llOgNvt8HuQjQvIyXM7v6jkmxI0=
-
 punycode@^2.1.0:
   version "2.1.1"
   resolved "https://registry.yarnpkg.com/punycode/-/punycode-2.1.1.tgz#b58b010ac40c22c5657616c8d2c2c02c7bf479ec"
@@ -3981,11 +4057,6 @@ qs@6.7.0:
   resolved "https://registry.yarnpkg.com/qs/-/qs-6.7.0.tgz#41dc1a015e3d581f1621776be31afb2876a9b1bc"
   integrity sha512-VCdBRNFTX1fyE7Nb6FYoURo/SPe62QCaAyzJvUjwRaIsc+NePBEniHlvxFmmX56+HZphIGtV0XeCirBtpDrTyQ==
 
-querystring@0.2.0:
-  version "0.2.0"
-  resolved "https://registry.yarnpkg.com/querystring/-/querystring-0.2.0.tgz#b209849203bb25df820da756e747005878521620"
-  integrity sha1-sgmEkgO7Jd+CDadW50cAWHhSFiA=
-
 queue-microtask@^1.2.2:
   version "1.2.3"
   resolved "https://registry.yarnpkg.com/queue-microtask/-/queue-microtask-1.2.3.tgz#4929228bbc724dfac43e0efb058caf7b6cfb6243"
@@ -4450,6 +4521,16 @@ schema-utils@^3.1.0, schema-utils@^3.1.1:
     ajv "^6.12.5"
     ajv-keywords "^3.5.2"
 
+schema-utils@^4.0.0:
+  version "4.0.0"
+  resolved "https://registry.yarnpkg.com/schema-utils/-/schema-utils-4.0.0.tgz#60331e9e3ae78ec5d16353c467c34b3a0a1d3df7"
+  integrity sha512-1edyXKgh6XnJsJSQ8mKWXnN/BVaIbFMLpouRUrXgVq7WYne5kw3MW7UPhO44uRXQSIpTSXoJbmrR2X0w9kUTyg==
+  dependencies:
+    "@types/json-schema" "^7.0.9"
+    ajv "^8.8.0"
+    ajv-formats "^2.1.1"
+    ajv-keywords "^5.0.0"
+
 section-iterator@^2.0.0:
   version "2.0.0"
   resolved "https://registry.yarnpkg.com/section-iterator/-/section-iterator-2.0.0.tgz#bf444d7afeeb94ad43c39ad2fb26151627ccba2a"
@@ -4460,7 +4541,7 @@ select-hose@^2.0.0:
   resolved "https://registry.yarnpkg.com/select-hose/-/select-hose-2.0.0.tgz#625d8658f865af43ec962bfc376a37359a4994ca"
   integrity sha1-Yl2GWPhlr0Psliv8N2o3NZpJlMo=
 
-selfsigned@^1.10.11, selfsigned@^1.10.8:
+selfsigned@^1.10.8, selfsigned@^2.0.0:
   version "1.10.11"
   resolved "https://registry.yarnpkg.com/selfsigned/-/selfsigned-1.10.11.tgz#24929cd906fe0f44b6d01fb23999a739537acbe9"
   integrity sha512-aVmbPOfViZqOZPgRBT0+3u4yZFHpmnIghLMlAcb5/xhp5ZtB/RVnKhz5vl2M32CLXAqR4kha9zfhNg0Lf/sxKA==
@@ -5158,14 +5239,6 @@ url-loader@^4.1.1:
     mime-types "^2.1.27"
     schema-utils "^3.0.0"
 
-url@^0.11.0:
-  version "0.11.0"
-  resolved "https://registry.yarnpkg.com/url/-/url-0.11.0.tgz#3838e97cfc60521eb73c525a8e55bfdd9e2e28f1"
-  integrity sha1-ODjpfPxgUh63PFJajlW/3Z4uKPE=
-  dependencies:
-    punycode "1.3.2"
-    querystring "0.2.0"
-
 util-deprecate@^1.0.1, util-deprecate@^1.0.2, util-deprecate@~1.0.1:
   version "1.0.2"
   resolved "https://registry.yarnpkg.com/util-deprecate/-/util-deprecate-1.0.2.tgz#450d4dc9fa70de732762fbd2d4a28981419a0ccf"
@@ -5278,46 +5351,50 @@ webpack-cli@^4.8.0:
     v8-compile-cache "^2.2.0"
     webpack-merge "^5.7.3"
 
-webpack-dev-middleware@^5.2.1:
-  version "5.2.1"
-  resolved "https://registry.yarnpkg.com/webpack-dev-middleware/-/webpack-dev-middleware-5.2.1.tgz#97c948144349177856a3d2d9c612cc3fee180cf1"
-  integrity sha512-Kx1X+36Rn9JaZcQMrJ7qN3PMAuKmEDD9ZISjUj3Cgq4A6PtwYsC4mpaKotSRYH3iOF6HsUa8viHKS59FlyVifQ==
+webpack-dev-middleware@^5.3.0:
+  version "5.3.0"
+  resolved "https://registry.yarnpkg.com/webpack-dev-middleware/-/webpack-dev-middleware-5.3.0.tgz#8fc02dba6e72e1d373eca361623d84610f27be7c"
+  integrity sha512-MouJz+rXAm9B1OTOYaJnn6rtD/lWZPy2ufQCH3BPs8Rloh/Du6Jze4p7AeLYHkVi0giJnYLaSGDC7S+GM9arhg==
   dependencies:
     colorette "^2.0.10"
     memfs "^3.2.2"
     mime-types "^2.1.31"
     range-parser "^1.2.1"
-    schema-utils "^3.1.0"
-
-webpack-dev-server@^4.3.0:
-  version "4.3.0"
-  resolved "https://registry.yarnpkg.com/webpack-dev-server/-/webpack-dev-server-4.3.0.tgz#732f5869d4c06e222b599daee64bc268f5edea24"
-  integrity sha512-kuqP9Xn4OzcKe7f0rJwd4p8xqiD+4b5Lzu8tJa8OttRL3E1Q8gI2KmUtouJTgDswjjvHOHlZDV8LTQfSY5qZSA==
-  dependencies:
+    schema-utils "^4.0.0"
+
+webpack-dev-server@^4.7.3:
+  version "4.7.3"
+  resolved "https://registry.yarnpkg.com/webpack-dev-server/-/webpack-dev-server-4.7.3.tgz#4e995b141ff51fa499906eebc7906f6925d0beaa"
+  integrity sha512-mlxq2AsIw2ag016nixkzUkdyOE8ST2GTy34uKSABp1c4nhjZvH90D5ZRR+UOLSsG4Z3TFahAi72a3ymRtfRm+Q==
+  dependencies:
+    "@types/bonjour" "^3.5.9"
+    "@types/connect-history-api-fallback" "^1.3.5"
+    "@types/serve-index" "^1.9.1"
+    "@types/sockjs" "^0.3.33"
+    "@types/ws" "^8.2.2"
     ansi-html-community "^0.0.8"
     bonjour "^3.5.0"
-    chokidar "^3.5.1"
+    chokidar "^3.5.2"
     colorette "^2.0.10"
     compression "^1.7.4"
     connect-history-api-fallback "^1.6.0"
+    default-gateway "^6.0.3"
     del "^6.0.0"
     express "^4.17.1"
     graceful-fs "^4.2.6"
     html-entities "^2.3.2"
     http-proxy-middleware "^2.0.0"
-    internal-ip "^6.2.0"
     ipaddr.js "^2.0.1"
     open "^8.0.9"
     p-retry "^4.5.0"
     portfinder "^1.0.28"
-    schema-utils "^3.1.0"
-    selfsigned "^1.10.11"
+    schema-utils "^4.0.0"
+    selfsigned "^2.0.0"
     serve-index "^1.9.1"
     sockjs "^0.3.21"
     spdy "^4.0.2"
     strip-ansi "^7.0.0"
-    url "^0.11.0"
-    webpack-dev-middleware "^5.2.1"
+    webpack-dev-middleware "^5.3.0"
     ws "^8.1.0"
 
 webpack-merge@^5.7.3:
```
