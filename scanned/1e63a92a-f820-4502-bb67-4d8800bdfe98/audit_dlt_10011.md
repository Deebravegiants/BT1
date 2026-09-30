# [?] Merge pull request #34 from PureStake/tgmichel-vulnerability-fix

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2020-09-24
Source: https://github.com/moonbeam-foundation/moonbeam/commit/34a29162af620809ef86dc8cd1bffde2f81fbfef
Type: security-commit

## Details
Merge pull request #34 from PureStake/tgmichel-vulnerability-fix

Fix serialize-javascript vulnerability alert

## Patch
### .github/workflows/tests.yml
```diff
@@ -9,13 +9,6 @@ jobs:
     - uses: actions/checkout@v2
     - name: Submodules
       run: git submodule update --init --recursive
-    - name: Cache Rust dependencies
-      uses: actions/cache@v1.1.2
-      with:
-        path: target
-        key: ${{ runner.OS }}-build-${{ hashFiles('**/Cargo.lock') }}
-        restore-keys: |
-          ${{ runner.OS }}-build-
     - name: Init
       run: |
         scripts/init.sh
```

### Cargo.lock
```diff
@@ -713,15 +713,6 @@ dependencies = [
  "bitflags",
 ]
 
-[[package]]
-name = "cloudabi"
-version = "0.1.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "4344512281c643ae7638bbabc3af17a11307803ec8f0fcad9fae512a8bf36467"
-dependencies = [
- "bitflags",
-]
-
 [[package]]
 name = "concurrent-queue"
 version = "1.2.2"
@@ -3385,15 +3376,6 @@ dependencies = [
  "scopeguard 1.1.0",
 ]
 
-[[package]]
-name = "lock_api"
-version = "0.4.1"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "28247cc5a5be2f05fbcd76dd0cf2c7d3b5400cb978a28042abcd4fa0b3f8261c"
-dependencies = [
- "scopeguard 1.1.0",
-]
-
 [[package]]
 name = "log"
 version = "0.3.9"
@@ -4821,17 +4803,6 @@ dependencies = [
  "parking_lot_core 0.7.2",
 ]
 
-[[package]]
-name = "parking_lot"
-version = "0.11.0"
-source = "registry+https://github.com/rust-lang/crates.io-index"
-checksum = "a4893845fa2ca272e647da5d0e46660a314ead9c2fdd9a883aabc32e481a8733"
-dependencies = [
- "instant",
- "lock_api 0.4.1",
- "parking_lot_core 0.8.0",
-]
-
 [[package]]
 name = "parking_lot_core"
 version = "0.4.0"
@@ -4852,7 +4823,7 @@ source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "b876b1b9e7ac6e1a74a6da34d25c42e17e8862aa409cbbbdcfc8d86c6f3bc62b"
 dependencies = [
  "cfg-if",
- "cloudabi 0.0.3",
+ "cloudabi",
  "libc",
  "redox_syscall",
  "rustc_version",
@@ -5857,7 +5828,7 @@ version = "0.5.6"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "c618c47cd3ebd209790115ab837de41425723956ad3ce2e6a7f09890947cacb9"
 dependencies = [
- "cloudabi 0.0.3",
+ "cloudabi",
  "fuchsia-cprng",
  "libc",
  "rand_core 0.3.1",
@@ -5985,7 +5956,7 @@ version = "0.1.3"
 source = "registry+https://github.com/rust-lang/crates.io-index"
 checksum = "7b75f676a1e053fc562eafbb47838d67c84801e38fc1ba459e8f180deabd5071"
 dependencies = [
- "cloudabi 0.0.3",
+ "cloudabi",
  "fuchsia-cprng",
  "libc",
  "rand_core 0.4.2",
```

### tests/package-lock.json
```diff
@@ -172,6 +172,11 @@
       "resolved": "https://registry.npmjs.org/@types/chai/-/chai-4.2.11.tgz",
       "integrity": "sha512-t7uW6eFafjO+qJ3BIV2gGUyZs27egcNRkUdalkud+Qa3+kg//f129iuOFivHDXQ+vnU3fDXuwgv0cqMCbcE8sw=="
     },
+    "@types/color-name": {
+      "version": "1.1.1",
+      "resolved": "https://registry.npmjs.org/@types/color-name/-/color-name-1.1.1.tgz",
+      "integrity": "sha512-rr+OQyAjxze7GgWrSaJwydHStIhHq2lvY3BOC2Mj7KnzI7XK0Uw1TOOdI9lDoajEbSWLiYgoo4f1R51erQfhPQ=="
+    },
     "@types/mocha": {
       "version": "8.0.0",
       "resolved": "https://registry.npmjs.org/@types/mocha/-/mocha-8.0.0.tgz",
@@ -213,11 +218,12 @@
       "integrity": "sha1-7QMXwyIGT3lGbAKWa922Bas32Zg="
     },
     "ansi-styles": {
-      "version": "3.2.1",
-      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-3.2.1.tgz",
-      "integrity": "sha512-VT0ZI6kZRdTh8YyJw3SMbYm/u+NqfsAxEpWO0Pf9sq8/e94WxxOpPKx9FR1FlyCtOVDNOQ+8ntlqFxiRc+r5qA==",
+      "version": "4.2.1",
+      "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-4.2.1.tgz",
+      "integrity": "sha512-9VGjrMsG1vePxcSweQsN20KY/c4zN0h9fLjqAbwbPfahM3t+NL+M9HC8xeXG2I8pX5NoamTGNuomEUFI7fcUjA==",
       "requires": {
-        "color-convert": "^1.9.0"
+        "@types/color-name": "^1.1.1",
+        "color-convert": "^2.0.1"
       }
     },
     "anymatch": {
@@ -565,23 +571,12 @@
       }
     },
     "chalk": {
-      "version": "2.4.2",
-      "resolved": "https://registry.npmjs.org/chalk/-/chalk-2.4.2.tgz",
-      "integrity": "sha512-Mti+f9lpJNcwF4tWV8/OrTTtF1gZi+f8FqlyAdouralcFWFQWF2+NgCHShjkCb+IFBLq9buZwE1xckQU4peSuQ==",
+      "version": "4.1.0",
+      "resolved": "https://registry.npmjs.org/chalk/-/chalk-4.1.0.tgz",
+      "integrity": "sha512-qwx12AxXe2Q5xQ43Ac//I6v5aXTipYrSESdOgzrN+9XjgEpyjpKuvSGaN4qE93f7TQTlerQQ8S+EQ0EyDoVL1A==",
       "requires": {
-        "ansi-styles": "^3.2.1",
-        "escape-string-regexp": "^1.0.5",
-        "supports-color": "^5.3.0"
-      },
-      "dependencies": {
-        "supports-color": {
-          "version": "5.5.0",
-          "resolved": "https://registry.npmjs.org/supports-color/-/supports-color-5.5.0.tgz",
-          "integrity": "sha512-QjVjwdXIt408MIiAqCX4oUKsgU2EqAGzs2Ppkm4aQYbjm+ZEWEcW4SfFNTr4uMNZma0ey4f5lgLrkB0aX0QMow==",
-          "requires": {
-            "has-flag": "^3.0.0"
-          }
-        }
+        "ansi-styles": "^4.1.0",
+        "supports-color": "^7.1.0"
       }
     },
     "check-error": {
@@ -590,9 +585,9 @@
       "integrity": "sha1-V00xLt2Iu13YkS6Sht1sCu1KrII="
     },
     "chokidar": {
-      "version": "3.3.1",
-      "resolved": "https://registry.npmjs.org/chokidar/-/chokidar-3.3.1.tgz",
-      "integrity": "sha512-4QYCEWOcK3OJrxwvyyAOxFuhpvOVCYkr33LPfFNBjAD/w3sEzWsp2BUOkI4l9bHvWioAd0rc6NlHUOEaWkTeqg==",
+      "version": "3.4.2",
+      "resolved": "https://registry.npmjs.org/chokidar/-/chokidar-3.4.2.tgz",
+      "integrity": "sha512-IZHaDeBeI+sZJRX7lGcXsdzgvZqKv6sECqsbErJA4mHWfpRrD8B97kSFN4cQz6nGBGiuFia1MKR4d6c1o8Cv7A==",
       "requires": {
         "anymatch": "~3.1.1",
         "braces": "~3.0.2",
@@ -601,7 +596,7 @@
         "is-binary-path": "~2.1.0",
         "is-glob": "~4.0.1",
         "normalize-path": "~3.0.0",
-        "readdirp": "~3.3.0"
+        "readdirp": "~3.4.0"
       }
     },
     "chownr": {
@@ -690,17 +685,17 @@
       }
     },
     "color-convert": {
-      "version": "1.9.3",
-      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-1.9.3.tgz",
-      "integrity": "sha512-QfAUtd+vFdAtFQcC8CCyYt1fYWxSqAiK2cSD6zDB8N3cpsEBAvRxp9zOGg6G/SHHJYAT88/az/IuDGALsNVbGg==",
+      "version": "2.0.1",
+      "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-2.0.1.tgz",
+      "integrity": "sha512-RRECPsj7iu/xb5oKYcsFHSppFNnsj/52OVTRKb4zP5onXwVF3zVmmToNcOfGC+CRDpfK/U584fMg38ZHCaElKQ==",
       "requires": {
-        "color-name": "1.1.3"
+        "color-name": "~1.1.4"
       }
     },
     "color-name": {
-      "version": "1.1.3",
-      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.3.tgz",
-      "integrity": "sha1-p9BVi9icQveV3UIyj3QIMcpTvCU="
+      "version": "1.1.4",
+      "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.4.tgz",
+      "integrity": "sha512-dOy+3AuW3a2wNbZHIuMZpTcgjGuLU/uBL/ubcZF9OXbDo8ff4O8yVp5Bf0efS8uEoYo5q4Fx7dY9OgQGXgAsQA=="
     },
     "combined-stream": {
       "version": "1.0.8",
@@ -1070,9 +1065,9 @@
       "integrity": "sha1-Aljq5NPQwJdN4cFpGI7wBR0dGYg="
     },
     "escape-string-regexp": {
-      "version": "1.0.5",
-      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-1.0.5.tgz",
-      "integrity": "sha1-G2HAViGQqN/2rjuyzwIAyhMLhtQ="
+      "version": "4.0.0",
+      "resolved": "https://registry.npmjs.org/escape-string-regexp/-/escape-string-regexp-4.0.0.tgz",
+      "integrity": "sha512-TtpcNJ3XAzx3Gq8sWRzJaVajRs0uVxA2YAkdb1jm2YkPz4G6egUFAyA3n5vtEIZefPk5Wa4UXbKuS5fKkJWdgA=="
     },
     "esprima": {
       "version": "4.0.1",
@@ -1288,11 +1283,11 @@
       }
     },
     "find-up": {
-      "version": "4.1.0",
-      "resolved": "https://registry.npmjs.org/find-up/-/find-up-4.1.0.tgz",
-      "integrity": "sha512-PpOwAdQ/YlXQ2vj8a3h8IipDuYRi3wceVQQGYWxNINccq40Anw7BlsEXCMbt1Zt+OLA6Fq9suIpIWD0OsnISlw==",
+      "version": "5.0.0",
+      "resolved": "https://registry.npmjs.org/find-up/-/find-up-5.0.0.tgz",
+      "integrity": "sha512-78/PXT1wlLLDgTzDs7sjq9hzz0vXD+zn+7wypEe4fXQxCmdmqfGsEPQxmiCSQI3ajFV91bVSsvNtrJRiW6nGng==",
       "requires": {
-        "locate-path": "^5.0.0",
+        "locate-path": "^6.0.0",
         "path-exists": "^4.0.0"
       }
     },
@@ -1470,9 +1465,9 @@
       }
     },
     "has-flag": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-3.0.0.tgz",
-      "integrity": "sha1-tdRU3CGZriJWmfNGfloH87lVuv0="
+      "version": "4.0.0",
+      "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
+      "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ=="
     },
     "has-symbol-support-x": {
       "version": "1.4.2",
@@ -1638,9 +1633,9 @@
       "integrity": "sha512-Kq1rokWXOPXWuaMAqZiJW4XxsmD9zGx9q4aePabbn3qCRGedtH7Cm+zV8WETitMfu1wdh+Rvd6w5egwSngUX2A=="
     },
     "is-callable": {
-      "version": "1.2.0",
-      "resolved": "https://registry.npmjs.org/is-callable/-/is-callable-1.2.0.tgz",
-      "integrity": "sha512-pyVD9AaGLxtg6srb2Ng6ynWJqkHU9bEM087AKck0w8QwDarTfNcpIYoU8x8Hv2Icm8u6kFJM18Dag8lyqGkviw=="
+      "version": "1.2.2",
+      "resolved": "https://registry.npmjs.org/is-callable/-/is-callable-1.2.2.tgz",
+      "integrity": "sha512-dnMqspv5nU3LoewK2N/y7KLtxtakvTuaCsU9FU50/QDmdbHNy/4/JuRtMHqRU22o3q+W89YQndQEeCVwK+3qrA=="
     },
     "is-date-object": {
       "version": "1.0.2",
@@ -1696,9 +1691,9 @@
       "integrity": "sha1-caUMhCnfync8kqOQpKA7OfzVHT4="
     },
     "is-regex": {
-      "version": "1.1.0",
-      "resolved": "https://registry.npmjs.org/is-regex/-/is-regex-1.1.0.tgz",
-      "integrity": "sha512-iI97M8KTWID2la5uYXlkbSDQIg4F6o1sYboZKKTDpnDQMLtUL86zxhgDet3Q2SriaYsyGqZ6Mn2SjbRKeLHdqw==",
+      "version": "1.1.1",
+      "resolved": "https://registry.npmjs.org/is-regex/-/is-regex-1.1.1.tgz",
+      "integrity": "sha512-1+QkEcxiLlB7VEyFtyBg94e08OAsvq7FUBgApTq/w2ymCLyKJgDPsybBENVtA7XCQEgEXxKPonG+mvYRxh/LIg==",
       "requires": {
         "has-symbols": "^1.0.1"
       }
@@ -1780,9 +1775,9 @@
       "integrity": "sha512-gF1cRrHhIzNfToc802P800N8PpXS+evLLXfsVpowqmAFR9uwbi89WvXg2QspOmXL8QL86J4T1EpFu+yUkwJY3Q=="
     },
     "js-yaml": {
-      "version": "3.13.1",
-      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-3.13.1.tgz",
-      "integrity": "sha512-YfbcO7jXDdyj0DGxYVSlSeQNHbD7XPWvrVWeVUujrQEoZzWJIRrCPoyk6kL6IAjAG2IolMK4T0hNUe0HOUs5Jw==",
+      "version": "3.14.0",
+      "resolved": "https://registry.npmjs.org/js-yaml/-/js-yaml-3.14.0.tgz",
+      "integrity": "sha512-/4IbIeHcD9VMHFqDR/gQ7EdZdLimOvW2DdcxFjdyyZ9NsbS+ccrXqVWDtab/lRl5AlUqmpBx8EhPaWR+OtY17A==",
       "requires": {
         "argparse": "^1.0.7",
         "esprima": "^4.0.0"
@@ -1859,24 +1854,19 @@
       }
     },
     "locate-path": {
-      "version": "5.0.0",
-      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-5.0.0.tgz",
-      "integrity": "sha512-t7hw9pI+WvuwNJXwk5zVHpyhIqzg2qTlklJOf0mVxGSbe3Fp2VieZcduNYjaLDoy6p9uGpQEGWG87WpMKlNq8g==",
+      "version": "6.0.0",
+      "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-6.0.0.tgz",
+      "integrity": "sha512-iPZK6eYjbxRu3uB4/WZ3EsEIMJFMqAoopl3R+zuq0UjcAm/MO6KCweDgPfP3elTztoKP3KtnVHxTn2NHBSDVUw==",
       "requires": {
-        "p-locate": "^4.1.0"
+        "p-locate": "^5.0.0"
       }
     },
-    "lodash": {
-      "version": "4.17.19",
-      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.19.tgz",
-      "integrity": "sha512-JNvd8XER9GQX0v2qJgsaN/mzFCNA5BRe/j8JN9d+tWyGLSodKQHKFicdwNYzWwI3wjRnaKPsGj1XkBjx/F96DQ=="
-    },
     "log-symbols": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/log-symbols/-/log-symbols-3.0.0.tgz",
-      "integrity": "sha512-dSkNGuI7iG3mfvDzUuYZyvk5dD9ocYCYzNU6CYDE6+Xqd+gwme6Z00NS3dUh8mq/73HaEtT7m6W+yUPtU6BZnQ==",
+      "version": "4.0.0",
+      "resolved": "https://registry.npmjs.org/log-symbols/-/log-symbols-4.0.0.tgz",
+      "integrity": "sha512-FN8JBzLx6CzeMrB0tg6pqlGU1wCrXW+ZXGH481kfsBqer0hToTIiHdjH4Mq8xJUbvATujKCvaREGWpGUionraA==",
       "requires": {
-        "chalk": "^2.4.2"
+        "chalk": "^4.0.0"
       }
     },
     "lowercase-keys": {
@@ -2008,41 +1998,41 @@
       }
     },
     "mocha": {
-      "version": "8.0.1",
-      "resolved": "https://registry.npmjs.org/mocha/-/mocha-8.0.1.tgz",
-      "integrity": "sha512-vefaXfdYI8+Yo8nPZQQi0QO2o+5q9UIMX1jZ1XMmK3+4+CQjc7+B0hPdUeglXiTlr8IHMVRo63IhO9Mzt6fxOg==",
+      "version": "8.1.3",
+      "resolved": "https://registry.npmjs.org/mocha/-/mocha-8.1.3.tgz",
+      "integrity": "sha512-ZbaYib4hT4PpF4bdSO2DohooKXIn4lDeiYqB+vTmCdr6l2woW0b6H3pf5x4sM5nwQMru9RvjjHYWVGltR50ZBw==",
       "requires": {
         "ansi-colors": "4.1.1",
         "browser-stdout": "1.3.1",
-        "chokidar": "3.3.1",
-        "debug": "3.2.6",
+        "chokidar": "3.4.2",
+        "debug": "4.1.1",
         "diff": "4.0.2",
-        "escape-string-regexp": "1.0.5",
-        "find-up": "4.1.0",
+        "escape-string-regexp": "4.0.0",
+        "find-up": "5.0.0",
         "glob": "7.1.6",
         "growl": "1.10.5",
         "he": "1.2.0",
-        "js-yaml": "3.13.1",
-        "log-symbols": "3.0.0",
+        "js-yaml": "3.14.0",
+        "log-symbols": "4.0.0",
         "minimatch": "3.0.4",
         "ms": "2.1.2",
         "object.assign": "4.1.0",
         "promise.allsettled": "1.0.2",
-        "serialize-javascript": "3.0.0",
+        "serialize-javascript": "4.0.0",
         "strip-json-comments": "3.0.1",
         "supports-color": "7.1.0",
         "which": "2.0.2",
         "wide-align": "1.1.3",
         "workerpool": "6.0.0",
         "yargs": "13.3.2",
         "yargs-parser": "13.1.2",
-        "yargs-unparser": "1.6.0"
+        "yargs-unparser": "1.6.1"
       },
       "dependencies": {
         "debug": {
-          "version": "3.2.6",
-          "resolved": "https://registry.npmjs.org/debug/-/debug-3.2.6.tgz",
-          "integrity": "sha512-mel+jf7nrtEl5Pn1Qx46zARXKDpBbvzezse7p7LqINmdoIk8PYP5SySaxEmYv6TZ0JyEKA1hsCId6DIhgITtWQ==",
+          "version": "4.1.1",
+          "resolved": "https://registry.npmjs.org/debug/-/debug-4.1.1.tgz",
+          "integrity": "sha512-pYAIzeRo8J6KPEaJ0VWOh5Pzkbw/RetuzehGM7QRRX5he4fPHx2rdKMB256ehJCkX+XRQm16eZLqLNS8RSZXZw==",
           "requires": {
             "ms": "^2.1.1"
           }
@@ -2219,19 +2209,19 @@
       "integrity": "sha1-P7z7FbiZpEEjs0ttzBi3JDNqLK4="
     },
     "p-limit": {
-      "version": "2.3.0",
-      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-2.3.0.tgz",
-      "integrity": "sha512-//88mFWSJx8lxCzwdAABTJL2MyWB12+eIY7MDL2SqLmAkeKU9qxRvWuSyTjm3FUmpBEMuFfckAIqEaVGUDxb6w==",
+      "version": "3.0.2",
+      "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-3.0.2.tgz",
+      "integrity": "sha512-iwqZSOoWIW+Ew4kAGUlN16J4M7OB3ysMLSZtnhmqx7njIHFPlxWBX8xo3lVTyFVq6mI/lL9qt2IsN1sHwaxJkg==",
       "requires": {
         "p-try": "^2.0.0"
       }
     },
     "p-locate": {
-      "version": "4.1.0",
-      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-4.1.0.tgz",
-      "integrity": "sha512-R79ZZ/0wAxKGu3oYMlz8jy/kbhsNrS7SKZ7PxEHBgJ5+F2mtFW2fK2cOtBh1cHYkQsbzFV7I+EoRKe6Yt0oK7A==",
+      "version": "5.0.0",
+      "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-5.0.0.tgz",
+      "integrity": "sha512-LaNjtRWUBY++zB5nE/NwcaoMylSPk+S+ZHNB1TzdbMJMny6dynpAGt7X/tl/QYq3TIeE6nxHppbo2LGymrG5Pw==",
       "requires": {
-        "p-limit": "^2.2.0"
+        "p-limit": "^3.0.2"
       }
     },
     "p-timeout": {
@@ -2434,11 +2424,11 @@
       }
     },
     "readdirp": {
-      "version": "3.3.0",
-      "resolved": "https://registry.npmjs.org/readdirp/-/readdirp-3.3.0.tgz",
-      "integrity": "sha512-zz0pAkSPOXXm1viEwygWIPSPkcBYjW1xU5j/JBh5t9bGCJwa6f9+BJa6VaB2g+b55yVrmXzqkyLf4xaWYM0IkQ==",
+      "version": "3.4.0",
+      "resolved": "https://registry.npmjs.org/readdirp/-/readdirp-3.4.0.tgz",
+      "integrity": "sha512-0xe001vZBnJEK+uKcj8qOhyAKPzIT+gStxWr3LCB0DwcXR5NZJ3IaC+yGnHCYzB/S7ov3m3EEbZI2zeNvX+hGQ==",
       "requires": {
-        "picomatch": "^2.0.7"
+        "picomatch": "^2.2.1"
       }
     },
     "request": {
@@ -2576,9 +2566,12 @@
       }
     },
     "serialize-javascript": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/serialize-javascript/-/serialize-javascript-3.0.0.tgz",
-      "integrity": "sha512-skZcHYw2vEX4bw90nAr2iTTsz6x2SrHEnfxgKYmZlvJYBEZrvbKtobJWlQ20zczKb3bsHHXXTYt48zBA7ni9cw=="
+      "version": "4.0.0",
+      "resolved": "https://registry.npmjs.org/serialize-javascript/-/serialize-javascript-4.0.0.tgz",
+      "integrity": "sha512-GaNA54380uFefWghODBWEGisLZFj00nS5ACs6yHa9nLqlLpVLO8ChDGeKRjZnV4Nh4n0Qi7nhYZD/9fCPzEqkw==",
+      "requires": {
+        "randombytes": "^2.1.0"
+      }
     },
     "serve-static": {
       "version": "1.14.1",
@@ -2756,13 +2749,6 @@
       "integrity": "sha512-oRSIpR8pxT1Wr2FquTNnGet79b3BWljqOuoW/h4oBhxJ/HUbX5nX6JSruTkvXDCFMwDPvsaTTbvMLKZWSy0R5g==",
       "requires": {
         "has-flag": "^4.0.0"
-      },
-      "dependencies": {
-        "has-flag": {
-          "version": "4.0.0",
-          "resolved": "https://registry.npmjs.org/has-flag/-/has-flag-4.0.0.tgz",
-          "integrity": "sha512-EykJT/Q1KjTWctppgIAgfSO0tKVuZUjhgMr17kqTumMl6Afv3EISleU7qZUzoXDFTAHTDC4NOoG/ZxU3EvlMPQ=="
-        }
       }
     },
     "swarm-js": {
@@ -3403,6 +3389,27 @@
           "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-4.1.0.tgz",
           "integrity": "sha512-1apePfXM1UOSqw0o9IiFAovVz9M5S1Dg+4TrDwfMewQ6p/rmMueb7tWZjQ1rx4Loy1ArBggoqGpfqqdI4rondg=="
         },
+        "ansi-styles": {
+          "version": "3.2.1",
+          "resolved": "https://registry.npmjs.org/ansi-styles/-/ansi-styles-3.2.1.tgz",
+          "integrity": "sha512-VT0ZI6kZRdTh8YyJw3SMbYm/u+NqfsAxEpWO0Pf9sq8/e94WxxOpPKx9FR1FlyCtOVDNOQ+8ntlqFxiRc+r5qA==",
+          "requires": {
+            "color-convert": "^1.9.0"
+          }
+        },
+        "color-convert": {
+          "version": "1.9.3",
+          "resolved": "https://registry.npmjs.org/color-convert/-/color-convert-1.9.3.tgz",
+          "integrity": "sha512-QfAUtd+vFdAtFQcC8CCyYt1fYWxSqAiK2cSD6zDB8N3cpsEBAvRxp9zOGg6G/SHHJYAT88/az/IuDGALsNVbGg==",
+          "requires": {
+            "color-name": "1.1.3"
+          }
+        },
+        "color-name": {
+          "version": "1.1.3",
+          "resolved": "https://registry.npmjs.org/color-name/-/color-name-1.1.3.tgz",
+          "integrity": "sha1-p9BVi9icQveV3UIyj3QIMcpTvCU="
+        },
         "string-width": {
           "version": "3.1.0",
           "resolved": "https://registry.npmjs.org/string-width/-/string-width-3.1.0.tgz",
@@ -3538,6 +3545,14 @@
             "path-exists": "^3.0.0"
           }
         },
+        "p-limit": {
+          "version": "2.3.0",
+          "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-2.3.0.tgz",
+          "integrity": "sha512-//88mFWSJx8lxCzwdAABTJL2MyWB12+eIY7MDL2SqLmAkeKU9qxRvWuSyTjm3FUmpBEMuFfckAIqEaVGUDxb6w==",
+          "requires": {
+            "p-try": "^2.0.0"
+          }
+        },
         "p-locate": {
           "version": "3.0.0",
           "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-3.0.0.tgz",
@@ -3581,13 +3596,105 @@
       }
     },
     "yargs-unparser": {
-      "version": "1.6.0",
-      "resolved": "https://registry.npmjs.org/yargs-unparser/-/yargs-unparser-1.6.0.tgz",
-      "integrity": "sha512-W9tKgmSn0DpSatfri0nx52Joq5hVXgeLiqR/5G0sZNDoLZFOr/xjBUDcShCOGNsBnEMNo1KAMBkTej1Hm62HTw==",
+      "version": "1.6.1",
+      "resolved": "https://registry.npmjs.org/yargs-unparser/-/yargs-unparser-1.6.1.tgz",
+      "integrity": "sha512-qZV14lK9MWsGCmcr7u5oXGH0dbGqZAIxTDrWXZDo5zUr6b6iUmelNKO6x6R1dQT24AH3LgRxJpr8meWy2unolA==",
       "requires": {
+        "camelcase": "^5.3.1",
+        "decamelize": "^1.2.0",
         "flat": "^4.1.0",
-        "lodash": "^4.17.15",
-        "yargs": "^13.3.0"
+        "is-plain-obj": "^1.1.0",
+        "yargs": "^14.2.3"
+      },
+      "dependencies": {
+        "ansi-regex": {
+          "version": "4.1.0",
+          "resolved": "https://registry.npmjs.org/ansi-regex/-/ansi-regex-4.1.0.tgz",
+          "integrity": "sha512-1apePfXM1UOSqw0o9IiFAovVz9M5S1Dg+4TrDwfMewQ6p/rmMueb7tWZjQ1rx4Loy1ArBggoqGpfqqdI4rondg=="
+        },
+        "find-up": {
+          "version": "3.0.0",
+          "resolved": "https://registry.npmjs.org/find-up/-/find-up-3.0.0.tgz",
+          "integrity": "sha512-1yD6RmLI1XBfxugvORwlck6f75tYL+iR0jqwsOrOxMZyGYqUuDhJ0l4AXdO1iX/FTs9cBAMEk1gWSEx1kSbylg==",
+          "requires": {
+            "locate-path": "^3.0.0"
+          }
+        },
+        "locate-path": {
+          "version": "3.0.0",
+          "resolved": "https://registry.npmjs.org/locate-path/-/locate-path-3.0.0.tgz",
+          "integrity": "sha512-7AO748wWnIhNqAuaty2ZWHkQHRSNfPVIsPIfwEOWO22AmaoVrWavlOcMR5nzTLNYvp36X220/maaRsrec1G65A==",
+          "requires": {
+            "p-locate": "^3.0.0",
+            "path-exists": "^3.0.0"
+          }
+        },
+        "p-limit": {
+          "version": "2.3.0",
+          "resolved": "https://registry.npmjs.org/p-limit/-/p-limit-2.3.0.tgz",
+          "integrity": "sha512-//88mFWSJx8lxCzwdAABTJL2MyWB12+eIY7MDL2SqLmAkeKU9qxRvWuSyTjm3FUmpBEMuFfckAIqEaVGUDxb6w==",
+          "requires": {
+            "p-try": "^2.0.0"
+          }
+        },
+        "p-locate": {
+          "version": "3.0.0",
+          "resolved": "https://registry.npmjs.org/p-locate/-/p-locate-3.0.0.tgz",
+          "integrity": "sha512-x+12w/To+4GFfgJhBEpiDcLozRJGegY+Ei7/z0tSLkMmxGZNybVMSfWj9aJn8Z5Fc7dBUNJOOVgPv2H7IwulSQ==",
+          "requires": {
+            "p-limit": "^2.0.0"
+          }
+        },
+        "path-exists": {
+          "version": "3.0.0",
+          "resolved": "https://registry.npmjs.org/path-exists/-/path-exists-3.0.0.tgz",
+          "integrity": "sha1-zg6+ql94yxiSXqfYENe1mwEP1RU="
+        },
+        "string-width": {
+          "version": "3.1.0",
+          "resolved": "https://registry.npmjs.org/string-width/-/string-width-3.1.0.tgz",
+          "integrity": "sha512-vafcv6KjVZKSgz06oM/H6GDBrAtz8vdhQakGjFIvNrHA6y3HCF1CInLy+QLq8dTJPQ1b+KDUqDFctkdRW44e1w==",
+          "requires": {
+            "emoji-regex": "^7.0.1",
+            "is-fullwidth-code-point": "^2.0.0",
+            "strip-ansi": "^5.1.0"
+          }
+        },
+        "strip-ansi": {
+          "version": "5.2.0",
+          "resolved": "https://registry.npmjs.org/strip-ansi/-/strip-ansi-5.2.0.tgz",
+          "integrity": "sha512-DuRs1gKbBqsMKIZlrffwlug8MHkcnpjs5VPmL1PAh+mA30U0DTotfDZ0d2UUsXpPmPmMMJ6W773MaA3J+lbiWA==",
+          "requires": {
+            "ansi-regex": "^4.1.0"
+          }
+        },
+        "yargs": {
+          "version": "14.2.3",
+          "resolved": "https://registry.npmjs.org/yargs/-/yargs-14.2.3.tgz",
+          "integrity": "sha512-ZbotRWhF+lkjijC/VhmOT9wSgyBQ7+zr13+YLkhfsSiTriYsMzkTUFP18pFhWwBeMa5gUc1MzbhrO6/VB7c9Xg==",
+          "requires": {
+            "cliui": "^5.0.0",
+            "decamelize": "^1.2.0",
+            "find-up": "^3.0.0",
+            "get-caller-file": "^2.0.1",
+            "require-directory": "^2.1.1",
+            "require-main-filename": "^2.0.0",
+            "set-blocking": "^2.0.0",
+            "string-width": "^3.0.0",
+            "which-module": "^2.0.0",
+            "y18n": "^4.0.0",
+            "yargs-parser": "^15.0.1"
+          }
+        },
+        "yargs-parser": {
+          "version": "15.0.1",
+          "resolved": "https://registry.npmjs.org/yargs-parser/-/yargs-parser-15.0.1.tgz",
+          "integrity": "sha512-0OAMV2mAZQrs3FkNpDQcBk1x5HXb8X4twADss4S0Iuk+2dGnLOE/fRHrsYm542GduMveyA77OF4wrNJuanRCWw==",
+          "requires": {
+            "camelcase": "^5.0.0",
+            "decamelize": "^1.2.0"
+          }
+        }
       }
     },
     "yn": {
```

### tests/package.json
```diff
@@ -12,7 +12,7 @@
     "@types/chai": "^4.2.11",
     "@types/mocha": "^8.0.0",
     "chai": "^4.2.0",
-    "mocha": "^8.0.1",
+    "mocha": "^8.1.3",
     "mocha-steps": "^1.3.0",
     "rimraf": "^3.0.2",
     "ts-node": "^8.10.2",
```
