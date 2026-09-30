# [?] chore: add npm overrides to fix security vulnerabilities

## Summary
Severity: Unknown
Chain: WalletConnect
Component: WalletConnect/walletconnect-monorepo
Published: 2026-01-28
Source: https://github.com/WalletConnect/walletconnect-monorepo/commit/4705628eff697aece9b104de4fe489ee82062cac
Type: security-commit

## Details
chore: add npm overrides to fix security vulnerabilities

Add overrides for transitive dependencies with known vulnerabilities:
- tar: ^7.5.7 (fixes arbitrary file overwrite via lerna)
- lodash: ^4.17.23 (fixes prototype pollution via wait-on)
- vite: ^7.3.1 (fixes server.fs.deny bypass via vitest)

This resolves 5 npm audit vulnerabilities (3 high, 2 moderate).

## Patch
### package-lock.json
```diff
@@ -4,6 +4,7 @@
   "requires": true,
   "packages": {
     "": {
+      "name": "walletconnect-monorepo",
       "license": "SEE LICENSE IN LICENSE.md",
       "workspaces": [
         "packages/types",
@@ -2102,6 +2103,23 @@
         "node": ">=18"
       }
     },
+    "node_modules/@esbuild/openharmony-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/openharmony-arm64/-/openharmony-arm64-0.27.2.tgz",
+      "integrity": "sha512-LRBbCmiU51IXfeXk59csuX/aSaToeG7w48nMwA6049Y4J4+VbWALAuXcs+qcD04rHDuSCSRKdmY63sruDS5qag==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "openharmony"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
     "node_modules/@esbuild/sunos-x64": {
       "version": "0.25.0",
       "resolved": "https://registry.npmjs.org/@esbuild/sunos-x64/-/sunos-x64-0.25.0.tgz",
@@ -3877,16 +3895,6 @@
         "node": "^20.17.0 || >=22.9.0"
       }
     },
-    "node_modules/@npmcli/arborist/node_modules/chownr": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/chownr/-/chownr-3.0.0.tgz",
-      "integrity": "sha512-+IxzY9BZOQd/XuYPRmrvEVjF/nqj5kgT4kEq7VofrDoM1MxoRjEWkrCC3EtLi59TVawxTAn+orJwFQcrqEN1+g==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/@npmcli/arborist/node_modules/minimatch": {
       "version": "10.1.1",
       "resolved": "https://registry.npmjs.org/minimatch/-/minimatch-10.1.1.tgz",
@@ -3998,33 +4006,6 @@
         "node": "^20.17.0 || >=22.9.0"
       }
     },
-    "node_modules/@npmcli/arborist/node_modules/tar": {
-      "version": "7.5.3",
-      "resolved": "https://registry.npmjs.org/tar/-/tar-7.5.3.tgz",
-      "integrity": "sha512-ENg5JUHUm2rDD7IvKNFGzyElLXNjachNLp6RaGf4+JOgxXHkqA+gq81ZAMCUmtMtqBsoU62lcp6S27g1LCYGGQ==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "dependencies": {
-        "@isaacs/fs-minipass": "^4.0.0",
-        "chownr": "^3.0.0",
-        "minipass": "^7.1.2",
-        "minizlib": "^3.1.0",
-        "yallist": "^5.0.0"
-      },
-      "engines": {
-        "node": ">=18"
-      }
-    },
-    "node_modules/@npmcli/arborist/node_modules/yallist": {
-      "version": "5.0.0",
-      "resolved": "https://registry.npmjs.org/yallist/-/yallist-5.0.0.tgz",
-      "integrity": "sha512-YgvUTfwqyc7UXVMrB+SImsVYSmTS8X/tSrtdNZMImM+n7+QTriRXyXim0mBrTXNeqzVF0KWGgHPeiyViFFrNDw==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/@npmcli/fs": {
       "version": "4.0.0",
       "resolved": "https://registry.npmjs.org/@npmcli/fs/-/fs-4.0.0.tgz",
@@ -10337,13 +10318,13 @@
       }
     },
     "node_modules/chownr": {
-      "version": "2.0.0",
-      "resolved": "https://registry.npmjs.org/chownr/-/chownr-2.0.0.tgz",
-      "integrity": "sha512-bIomtDF5KGpdogkLd9VspvFzk9KfpyyGlS8YFVZl7TGPBHL5snIOnxeshwVgPteQ9b4Eydl+pVbIyE1DcvCWgQ==",
+      "version": "3.0.0",
+      "resolved": "https://registry.npmjs.org/chownr/-/chownr-3.0.0.tgz",
+      "integrity": "sha512-+IxzY9BZOQd/XuYPRmrvEVjF/nqj5kgT4kEq7VofrDoM1MxoRjEWkrCC3EtLi59TVawxTAn+orJwFQcrqEN1+g==",
       "dev": true,
-      "license": "ISC",
+      "license": "BlueOak-1.0.0",
       "engines": {
-        "node": ">=10"
+        "node": ">=18"
       }
     },
     "node_modules/chrome-launcher": {
@@ -16098,9 +16079,9 @@
       }
     },
     "node_modules/lodash": {
-      "version": "4.17.21",
-      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.21.tgz",
-      "integrity": "sha512-v2kDEe57lecTulaDIuNTPy3Ry4gLGJ6Z1O3vE1krgXZNrsQ+LFTGHVxVjcXPs17LhbZVGedAJv8XZ1tvj5FvSg==",
+      "version": "4.17.23",
+      "resolved": "https://registry.npmjs.org/lodash/-/lodash-4.17.23.tgz",
+      "integrity": "sha512-LgVTMpQtIopCi79SJeDiP0TfWi5CNEc/L/aRdTh3yIvmZXTnheWpKjSZhnvMl8iXbC1tFg9gdHHDMLoV7CnG+w==",
       "dev": true,
       "license": "MIT"
     },
@@ -17126,6 +17107,7 @@
       "resolved": "https://registry.npmjs.org/mkdirp/-/mkdirp-1.0.4.tgz",
       "integrity": "sha512-vVqVZQyf3WLx2Shd0qJ9xuvqgAyKPLAiqITEtqW0oIUjzo3PePDd6fW9iFz30ef7Ysp/oiWqbhszeGWW2T6Gzw==",
       "license": "MIT",
+      "peer": true,
       "bin": {
         "mkdirp": "bin/cmd.js"
       },
@@ -17362,16 +17344,6 @@
         "node": "^18.17.0 || >=20.5.0"
       }
     },
-    "node_modules/node-gyp/node_modules/chownr": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/chownr/-/chownr-3.0.0.tgz",
-      "integrity": "sha512-+IxzY9BZOQd/XuYPRmrvEVjF/nqj5kgT4kEq7VofrDoM1MxoRjEWkrCC3EtLi59TVawxTAn+orJwFQcrqEN1+g==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/node-gyp/node_modules/glob": {
       "version": "10.5.0",
       "resolved": "https://registry.npmjs.org/glob/-/glob-10.5.0.tgz",
@@ -17478,23 +17450,6 @@
         "url": "https://github.com/sponsors/sindresorhus"
       }
     },
-    "node_modules/node-gyp/node_modules/tar": {
-      "version": "7.5.3",
-      "resolved": "https://registry.npmjs.org/tar/-/tar-7.5.3.tgz",
-      "integrity": "sha512-ENg5JUHUm2rDD7IvKNFGzyElLXNjachNLp6RaGf4+JOgxXHkqA+gq81ZAMCUmtMtqBsoU62lcp6S27g1LCYGGQ==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "dependencies": {
-        "@isaacs/fs-minipass": "^4.0.0",
-        "chownr": "^3.0.0",
-        "minipass": "^7.1.2",
-        "minizlib": "^3.1.0",
-        "yallist": "^5.0.0"
-      },
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/node-gyp/node_modules/unique-filename": {
       "version": "4.0.0",
       "resolved": "https://registry.npmjs.org/unique-filename/-/unique-filename-4.0.0.tgz",
@@ -17537,16 +17492,6 @@
         "node": "^18.17.0 || >=20.5.0"
       }
     },
-    "node_modules/node-gyp/node_modules/yallist": {
-      "version": "5.0.0",
-      "resolved": "https://registry.npmjs.org/yallist/-/yallist-5.0.0.tgz",
-      "integrity": "sha512-YgvUTfwqyc7UXVMrB+SImsVYSmTS8X/tSrtdNZMImM+n7+QTriRXyXim0mBrTXNeqzVF0KWGgHPeiyViFFrNDw==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/node-int64": {
       "version": "0.4.0",
       "resolved": "https://registry.npmjs.org/node-int64/-/node-int64-0.4.0.tgz",
@@ -18530,16 +18475,6 @@
         "node": "^18.17.0 || >=20.5.0"
       }
     },
-    "node_modules/pacote/node_modules/chownr": {
-      "version": "3.0.0",
-      "resolved": "https://registry.npmjs.org/chownr/-/chownr-3.0.0.tgz",
-      "integrity": "sha512-+IxzY9BZOQd/XuYPRmrvEVjF/nqj5kgT4kEq7VofrDoM1MxoRjEWkrCC3EtLi59TVawxTAn+orJwFQcrqEN1+g==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/pacote/node_modules/hosted-git-info": {
       "version": "8.1.0",
       "resolved": "https://registry.npmjs.org/hosted-git-info/-/hosted-git-info-8.1.0.tgz",
@@ -18612,23 +18547,6 @@
         "node": "^18.17.0 || >=20.5.0"
       }
     },
-    "node_modules/pacote/node_modules/tar": {
-      "version": "7.5.3",
-      "resolved": "https://registry.npmjs.org/tar/-/tar-7.5.3.tgz",
-      "integrity": "sha512-ENg5JUHUm2rDD7IvKNFGzyElLXNjachNLp6RaGf4+JOgxXHkqA+gq81ZAMCUmtMtqBsoU62lcp6S27g1LCYGGQ==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "dependencies": {
-        "@isaacs/fs-minipass": "^4.0.0",
-        "chownr": "^3.0.0",
-        "minipass": "^7.1.2",
-        "minizlib": "^3.1.0",
-        "yallist": "^5.0.0"
-      },
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/pacote/node_modules/which": {
       "version": "5.0.0",
       "resolved": "https://registry.npmjs.org/which/-/which-5.0.0.tgz",
@@ -18645,16 +18563,6 @@
         "node": "^18.17.0 || >=20.5.0"
       }
     },
-    "node_modules/pacote/node_modules/yallist": {
-      "version": "5.0.0",
-      "resolved": "https://registry.npmjs.org/yallist/-/yallist-5.0.0.tgz",
-      "integrity": "sha512-YgvUTfwqyc7UXVMrB+SImsVYSmTS8X/tSrtdNZMImM+n7+QTriRXyXim0mBrTXNeqzVF0KWGgHPeiyViFFrNDw==",
-      "dev": true,
-      "license": "BlueOak-1.0.0",
-      "engines": {
-        "node": ">=18"
-      }
-    },
     "node_modules/parent-module": {
       "version": "1.0.1",
       "resolved": "https://registry.npmjs.org/parent-module/-/parent-module-1.0.1.tgz",
@@ -21299,22 +21207,20 @@
       }
     },
     "node_modules/tar": {
-      "version": "6.2.1",
-      "resolved": "https://registry.npmjs.org/tar/-/tar-6.2.1.tgz",
-      "integrity": "sha512-DZ4yORTwrbTj/7MZYq2w+/ZFdI6OZ/f9SFHR+71gIVUZhOQPHzVCLpvRnPgyaMpfWxxk/4ONva3GQSyNIKRv6A==",
-      "deprecated": "Old versions of tar are not supported, and contain widely publicized security vulnerabilities, which have been fixed in the current version. Please update. Support for old versions may be purchased (at exhorbitant rates) by contacting i@izs.me",
+      "version": "7.5.7",
+      "resolved": "https://registry.npmjs.org/tar/-/tar-7.5.7.tgz",
+      "integrity": "sha512-fov56fJiRuThVFXD6o6/Q354S7pnWMJIVlDBYijsTNx6jKSE4pvrDTs6lUnmGvNyfJwFQQwWy3owKz1ucIhveQ==",
       "dev": true,
-      "license": "ISC",
+      "license": "BlueOak-1.0.0",
       "dependencies": {
-        "chownr": "^2.0.0",
-        "fs-minipass": "^2.0.0",
-        "minipass": "^5.0.0",
-        "minizlib": "^2.1.1",
-        "mkdirp": "^1.0.3",
-        "yallist": "^4.0.0"
+        "@isaacs/fs-minipass": "^4.0.0",
+        "chownr": "^3.0.0",
+        "minipass": "^7.1.2",
+        "minizlib": "^3.1.0",
+        "yallist": "^5.0.0"
       },
       "engines": {
-        "node": ">=10"
+        "node": ">=18"
       }
     },
     "node_modules/tar-stream": {
@@ -21334,67 +21240,14 @@
         "node": ">=6"
       }
     },
-    "node_modules/tar/node_modules/fs-minipass": {
-      "version": "2.1.0",
-      "resolved": "https://registry.npmjs.org/fs-minipass/-/fs-minipass-2.1.0.tgz",
-      "integrity": "sha512-V/JgOLFCS+R6Vcq0slCuaeWEdNC3ouDlJMNIsacH2VtALiu9mV4LPrHc5cDl8k5aw6J8jwgWWpiTo5RYhmIzvg==",
-      "dev": true,
-      "license": "ISC",
-      "dependencies": {
-        "minipass": "^3.0.0"
-      },
-      "engines": {
-        "node": ">= 8"
-      }
-    },
-    "node_modules/tar/node_modules/fs-minipass/node_modules/minipass": {
-      "version": "3.3.6",
-      "resolved": "https://registry.npmjs.org/minipass/-/minipass-3.3.6.tgz",
-      "integrity": "sha512-DxiNidxSEK+tHG6zOIklvNOwm3hvCrbUrdtzY74U6HKTJxvIDfOUL5W5P2Ghd3DTkhhKPYGqeNUIh5qcM4YBfw==",
-      "dev": true,
-      "license": "ISC",
-      "dependencies": {
-        "yallist": "^4.0.0"
-      },
-      "engines": {
-        "node": ">=8"
-      }
-    },
-    "node_modules/tar/node_modules/minipass": {
+    "node_modules/tar/node_modules/yallist": {
       "version": "5.0.0",
-      "resolved": "https://registry.npmjs.org/minipass/-/minipass-5.0.0.tgz",
-      "integrity": "sha512-3FnjYuehv9k6ovOEbyOswadCDPX1piCfhV8ncmYtHOjuPwylVWsghTLo7rabjC3Rx5xD4HDx8Wm1xnMF7S5qFQ==",
-      "dev": true,
-      "license": "ISC",
-      "engines": {
-        "node": ">=8"
-      }
-    },
-    "node_modules/tar/node_modules/minizlib": {
-      "version": "2.1.2",
-      "resolved": "https://registry.npmjs.org/minizlib/-/minizlib-2.1.2.tgz",
-      "integrity": "sha512-bAxsR8BVfj60DWXHE3u30oHzfl4G7khkSuPW+qvpd7jFRHm7dLxOjUk1EHACJ/hxLY8phGJ0YhYHZo7jil7Qdg==",
-      "dev": true,
-      "license": "MIT",
-      "dependencies": {
-        "minipass": "^3.0.0",
-        "yallist": "^4.0.0"
-      },
-      "engines": {
-        "node": ">= 8"
-      }
-    },
-    "node_modules/tar/node_modules/minizlib/node_modules/minipass": {
-      "version": "3.3.6",
-      "resolved": "https://registry.npmjs.org/minipass/-/minipass-3.3.6.tgz",
-      "integrity": "sha512-DxiNidxSEK+tHG6zOIklvNOwm3hvCrbUrdtzY74U6HKTJxvIDfOUL5W5P2Ghd3DTkhhKPYGqeNUIh5qcM4YBfw==",
+      "resolved": "https://registry.npmjs.org/yallist/-/yallist-5.0.0.tgz",
+      "integrity": "sha512-YgvUTfwqyc7UXVMrB+SImsVYSmTS8X/tSrtdNZMImM+n7+QTriRXyXim0mBrTXNeqzVF0KWGgHPeiyViFFrNDw==",
       "dev": true,
-      "license": "ISC",
-      "dependencies": {
-        "yallist": "^4.0.0"
-      },
+      "license": "BlueOak-1.0.0",
       "engines": {
-        "node": ">=8"
+        "node": ">=18"
       }
     },
     "node_modules/temp-dir": {
@@ -22424,76 +22277,543 @@
         "url": "https://opencollective.com/vitest"
       }
     },
-    "node_modules/vite-node/node_modules/@types/estree": {
-      "version": "1.0.8",
-      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.8.tgz",
-      "integrity": "sha512-dWHzHa2WqEXI/O1E9OjrocMTKJl2mSrEolh1Iomrv6U+JuNwaHXsXx9bLu5gG7BUWFIN0skIQJQ/L1rIex4X6w==",
-      "dev": true,
-      "license": "MIT"
-    },
-    "node_modules/vite-node/node_modules/@types/node": {
-      "version": "24.5.2",
-      "resolved": "https://registry.npmjs.org/@types/node/-/node-24.5.2.tgz",
-      "integrity": "sha512-FYxk1I7wPv3K2XBaoyH2cTnocQEu8AOZ60hPbsyukMPLv5/5qr7V1i8PLHdl6Zf87I+xZXFvPCXYjiTFq+YSDQ==",
+    "node_modules/vite-node/node_modules/@esbuild/aix-ppc64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/aix-ppc64/-/aix-ppc64-0.27.2.tgz",
+      "integrity": "sha512-GZMB+a0mOMZs4MpDbj8RJp4cw+w1WV5NYD6xzgvzUJ5Ek2jerwfO2eADyI6ExDSUED+1X8aMbegahsJi+8mgpw==",
+      "cpu": [
+        "ppc64"
+      ],
       "dev": true,
       "license": "MIT",
       "optional": true,
-      "peer": true,
-      "dependencies": {
-        "undici-types": "~7.12.0"
+      "os": [
+        "aix"
+      ],
+      "engines": {
+        "node": ">=18"
       }
     },
-    "node_modules/vite-node/node_modules/es-module-lexer": {
-      "version": "1.7.0",
-      "resolved": "https://registry.npmjs.org/es-module-lexer/-/es-module-lexer-1.7.0.tgz",
-      "integrity": "sha512-jEQoCwk8hyb2AZziIOLhDqpm5+2ww5uIE6lkO/6jcOCusfk6LhMHpXXfBLXTZ7Ydyt0j4VoUQv6uGNYbdW+kBA==",
-      "dev": true,
-      "license": "MIT"
-    },
-    "node_modules/vite-node/node_modules/fdir": {
-      "version": "6.5.0",
-      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
-      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
+    "node_modules/vite-node/node_modules/@esbuild/android-arm": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-arm/-/android-arm-0.27.2.tgz",
+      "integrity": "sha512-DVNI8jlPa7Ujbr1yjU2PfUSRtAUZPG9I1RwW4F4xFB1Imiu2on0ADiI/c3td+KmDtVKNbi+nffGDQMfcIMkwIA==",
+      "cpu": [
+        "arm"
+      ],
       "dev": true,
       "license": "MIT",
+      "optional": true,
+      "os": [
+        "android"
+      ],
       "engines": {
-        "node": ">=12.0.0"
-      },
-      "peerDependencies": {
-        "picomatch": "^3 || ^4"
-      },
-      "peerDependenciesMeta": {
-        "picomatch": {
-          "optional": true
-        }
+        "node": ">=18"
       }
     },
-    "node_modules/vite-node/node_modules/picomatch": {
-      "version": "4.0.3",
-      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.3.tgz",
-      "integrity": "sha512-5gTmgEY/sqK6gFXLIsQNH19lWb4ebPDLA4SdLP7dsWkIXHWlG66oPuVvXSGFPppYZz8ZDZq0dYYrbHfBCVUb1Q==",
+    "node_modules/vite-node/node_modules/@esbuild/android-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-arm64/-/android-arm64-0.27.2.tgz",
+      "integrity": "sha512-pvz8ZZ7ot/RBphf8fv60ljmaoydPU12VuXHImtAs0XhLLw+EXBi2BLe3OYSBslR4rryHvweW5gmkKFwTiFy6KA==",
+      "cpu": [
+        "arm64"
+      ],
       "dev": true,
       "license": "MIT",
+      "optional": true,
+      "os": [
+        "android"
+      ],
       "engines": {
-        "node": ">=12"
-      },
-      "funding": {
-        "url": "https://github.com/sponsors/jonschlinkert"
+        "node": ">=18"
       }
     },
-    "node_modules/vite-node/node_modules/rollup": {
-      "version": "4.52.2",
-      "resolved": "https://registry.npmjs.org/rollup/-/rollup-4.52.2.tgz",
-      "integrity": "sha512-I25/2QgoROE1vYV+NQ1En9T9UFB9Cmfm2CJ83zZOlaDpvz29wGQSZXWKw7MiNXau7wYgB/T9fVIdIuEQ+KbiiA==",
+    "node_modules/vite-node/node_modules/@esbuild/android-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-x64/-/android-x64-0.27.2.tgz",
+      "integrity": "sha512-z8Ank4Byh4TJJOh4wpz8g2vDy75zFL0TlZlkUkEwYXuPSgX8yzep596n6mT7905kA9uHZsf/o2OJZubl2l3M7A==",
+      "cpu": [
+        "x64"
+      ],
       "dev": true,
       "license": "MIT",
-      "dependencies": {
-        "@types/estree": "1.0.8"
-      },
-      "bin": {
-        "rollup": "dist/bin/rollup"
-      },
-      "engines": {
+      "optional": true,
+      "os": [
+        "android"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/darwin-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/darwin-arm64/-/darwin-arm64-0.27.2.tgz",
+      "integrity": "sha512-davCD2Zc80nzDVRwXTcQP/28fiJbcOwvdolL0sOiOsbwBa72kegmVU0Wrh1MYrbuCL98Omp5dVhQFWRKR2ZAlg==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "darwin"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/darwin-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/darwin-x64/-/darwin-x64-0.27.2.tgz",
+      "integrity": "sha512-ZxtijOmlQCBWGwbVmwOF/UCzuGIbUkqB1faQRf5akQmxRJ1ujusWsb3CVfk/9iZKr2L5SMU5wPBi1UWbvL+VQA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "darwin"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/freebsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/freebsd-arm64/-/freebsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-lS/9CN+rgqQ9czogxlMcBMGd+l8Q3Nj1MFQwBZJyoEKI50XGxwuzznYdwcav6lpOGv5BqaZXqvBSiB/kJ5op+g==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "freebsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/freebsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/freebsd-x64/-/freebsd-x64-0.27.2.tgz",
+      "integrity": "sha512-tAfqtNYb4YgPnJlEFu4c212HYjQWSO/w/h/lQaBK7RbwGIkBOuNKQI9tqWzx7Wtp7bTPaGC6MJvWI608P3wXYA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "freebsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-arm": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-arm/-/linux-arm-0.27.2.tgz",
+      "integrity": "sha512-vWfq4GaIMP9AIe4yj1ZUW18RDhx6EPQKjwe7n8BbIecFtCQG4CfHGaHuh7fdfq+y3LIA2vGS/o9ZBGVxIDi9hw==",
+      "cpu": [
+        "arm"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-arm64/-/linux-arm64-0.27.2.tgz",
+      "integrity": "sha512-hYxN8pr66NsCCiRFkHUAsxylNOcAQaxSSkHMMjcpx0si13t1LHFphxJZUiGwojB1a/Hd5OiPIqDdXONia6bhTw==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-ia32": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-ia32/-/linux-ia32-0.27.2.tgz",
+      "integrity": "sha512-MJt5BRRSScPDwG2hLelYhAAKh9imjHK5+NE/tvnRLbIqUWa+0E9N4WNMjmp/kXXPHZGqPLxggwVhz7QP8CTR8w==",
+      "cpu": [
+        "ia32"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-loong64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-loong64/-/linux-loong64-0.27.2.tgz",
+      "integrity": "sha512-lugyF1atnAT463aO6KPshVCJK5NgRnU4yb3FUumyVz+cGvZbontBgzeGFO1nF+dPueHD367a2ZXe1NtUkAjOtg==",
+      "cpu": [
+        "loong64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-mips64el": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-mips64el/-/linux-mips64el-0.27.2.tgz",
+      "integrity": "sha512-nlP2I6ArEBewvJ2gjrrkESEZkB5mIoaTswuqNFRv/WYd+ATtUpe9Y09RnJvgvdag7he0OWgEZWhviS1OTOKixw==",
+      "cpu": [
+        "mips64el"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-ppc64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-ppc64/-/linux-ppc64-0.27.2.tgz",
+      "integrity": "sha512-C92gnpey7tUQONqg1n6dKVbx3vphKtTHJaNG2Ok9lGwbZil6DrfyecMsp9CrmXGQJmZ7iiVXvvZH6Ml5hL6XdQ==",
+      "cpu": [
+        "ppc64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-riscv64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-riscv64/-/linux-riscv64-0.27.2.tgz",
+      "integrity": "sha512-B5BOmojNtUyN8AXlK0QJyvjEZkWwy/FKvakkTDCziX95AowLZKR6aCDhG7LeF7uMCXEJqwa8Bejz5LTPYm8AvA==",
+      "cpu": [
+        "riscv64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-s390x": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-s390x/-/linux-s390x-0.27.2.tgz",
+      "integrity": "sha512-p4bm9+wsPwup5Z8f4EpfN63qNagQ47Ua2znaqGH6bqLlmJ4bx97Y9JdqxgGZ6Y8xVTixUnEkoKSHcpRlDnNr5w==",
+      "cpu": [
+        "s390x"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/linux-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.27.2.tgz",
+      "integrity": "sha512-uwp2Tip5aPmH+NRUwTcfLb+W32WXjpFejTIOWZFw/v7/KnpCDKG66u4DLcurQpiYTiYwQ9B7KOeMJvLCu/OvbA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/netbsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/netbsd-arm64/-/netbsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-Kj6DiBlwXrPsCRDeRvGAUb/LNrBASrfqAIok+xB0LxK8CHqxZ037viF13ugfsIpePH93mX7xfJp97cyDuTZ3cw==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "netbsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/netbsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/netbsd-x64/-/netbsd-x64-0.27.2.tgz",
+      "integrity": "sha512-HwGDZ0VLVBY3Y+Nw0JexZy9o/nUAWq9MlV7cahpaXKW6TOzfVno3y3/M8Ga8u8Yr7GldLOov27xiCnqRZf0tCA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "netbsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/openbsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/openbsd-arm64/-/openbsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-DNIHH2BPQ5551A7oSHD0CKbwIA/Ox7+78/AWkbS5QoRzaqlev2uFayfSxq68EkonB+IKjiuxBFoV8ESJy8bOHA==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "openbsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/openbsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/openbsd-x64/-/openbsd-x64-0.27.2.tgz",
+      "integrity": "sha512-/it7w9Nb7+0KFIzjalNJVR5bOzA9Vay+yIPLVHfIQYG/j+j9VTH84aNB8ExGKPU4AzfaEvN9/V4HV+F+vo8OEg==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "openbsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/sunos-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/sunos-x64/-/sunos-x64-0.27.2.tgz",
+      "integrity": "sha512-kMtx1yqJHTmqaqHPAzKCAkDaKsffmXkPHThSfRwZGyuqyIeBvf08KSsYXl+abf5HDAPMJIPnbBfXvP2ZC2TfHg==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "sunos"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/win32-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-arm64/-/win32-arm64-0.27.2.tgz",
+      "integrity": "sha512-Yaf78O/B3Kkh+nKABUF++bvJv5Ijoy9AN1ww904rOXZFLWVc5OLOfL56W+C8F9xn5JQZa3UX6m+IktJnIb1Jjg==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/win32-ia32": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-ia32/-/win32-ia32-0.27.2.tgz",
+      "integrity": "sha512-Iuws0kxo4yusk7sw70Xa2E2imZU5HoixzxfGCdxwBdhiDgt9vX9VUCBhqcwY7/uh//78A1hMkkROMJq9l27oLQ==",
+      "cpu": [
+        "ia32"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@esbuild/win32-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-x64/-/win32-x64-0.27.2.tgz",
+      "integrity": "sha512-sRdU18mcKf7F+YgheI/zGf5alZatMUTKj/jNS6l744f9u3WFu4v7twcUI9vu4mknF4Y9aDlblIie0IM+5xxaqQ==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vite-node/node_modules/@types/estree": {
+      "version": "1.0.8",
+      "resolved": "https://registry.npmjs.org/@types/estree/-/estree-1.0.8.tgz",
+      "integrity": "sha512-dWHzHa2WqEXI/O1E9OjrocMTKJl2mSrEolh1Iomrv6U+JuNwaHXsXx9bLu5gG7BUWFIN0skIQJQ/L1rIex4X6w==",
+      "dev": true,
+      "license": "MIT"
+    },
+    "node_modules/vite-node/node_modules/@types/node": {
+      "version": "24.5.2",
+      "resolved": "https://registry.npmjs.org/@types/node/-/node-24.5.2.tgz",
+      "integrity": "sha512-FYxk1I7wPv3K2XBaoyH2cTnocQEu8AOZ60hPbsyukMPLv5/5qr7V1i8PLHdl6Zf87I+xZXFvPCXYjiTFq+YSDQ==",
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "peer": true,
+      "dependencies": {
+        "undici-types": "~7.12.0"
+      }
+    },
+    "node_modules/vite-node/node_modules/es-module-lexer": {
+      "version": "1.7.0",
+      "resolved": "https://registry.npmjs.org/es-module-lexer/-/es-module-lexer-1.7.0.tgz",
+      "integrity": "sha512-jEQoCwk8hyb2AZziIOLhDqpm5+2ww5uIE6lkO/6jcOCusfk6LhMHpXXfBLXTZ7Ydyt0j4VoUQv6uGNYbdW+kBA==",
+      "dev": true,
+      "license": "MIT"
+    },
+    "node_modules/vite-node/node_modules/esbuild": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/esbuild/-/esbuild-0.27.2.tgz",
+      "integrity": "sha512-HyNQImnsOC7X9PMNaCIeAm4ISCQXs5a5YasTXVliKv4uuBo1dKrG0A+uQS8M5eXjVMnLg3WgXaKvprHlFJQffw==",
+      "dev": true,
+      "hasInstallScript": true,
+      "license": "MIT",
+      "bin": {
+        "esbuild": "bin/esbuild"
+      },
+      "engines": {
+        "node": ">=18"
+      },
+      "optionalDependencies": {
+        "@esbuild/aix-ppc64": "0.27.2",
+        "@esbuild/android-arm": "0.27.2",
+        "@esbuild/android-arm64": "0.27.2",
+        "@esbuild/android-x64": "0.27.2",
+        "@esbuild/darwin-arm64": "0.27.2",
+        "@esbuild/darwin-x64": "0.27.2",
+        "@esbuild/freebsd-arm64": "0.27.2",
+        "@esbuild/freebsd-x64": "0.27.2",
+        "@esbuild/linux-arm": "0.27.2",
+        "@esbuild/linux-arm64": "0.27.2",
+        "@esbuild/linux-ia32": "0.27.2",
+        "@esbuild/linux-loong64": "0.27.2",
+        "@esbuild/linux-mips64el": "0.27.2",
+        "@esbuild/linux-ppc64": "0.27.2",
+        "@esbuild/linux-riscv64": "0.27.2",
+        "@esbuild/linux-s390x": "0.27.2",
+        "@esbuild/linux-x64": "0.27.2",
+        "@esbuild/netbsd-arm64": "0.27.2",
+        "@esbuild/netbsd-x64": "0.27.2",
+        "@esbuild/openbsd-arm64": "0.27.2",
+        "@esbuild/openbsd-x64": "0.27.2",
+        "@esbuild/openharmony-arm64": "0.27.2",
+        "@esbuild/sunos-x64": "0.27.2",
+        "@esbuild/win32-arm64": "0.27.2",
+        "@esbuild/win32-ia32": "0.27.2",
+        "@esbuild/win32-x64": "0.27.2"
+      }
+    },
+    "node_modules/vite-node/node_modules/fdir": {
+      "version": "6.5.0",
+      "resolved": "https://registry.npmjs.org/fdir/-/fdir-6.5.0.tgz",
+      "integrity": "sha512-tIbYtZbucOs0BRGqPJkshJUYdL+SDH7dVM8gjy+ERp3WAUjLEFJE+02kanyHtwjWOnwrKYBiwAmM0p4kLJAnXg==",
+      "dev": true,
+      "license": "MIT",
+      "engines": {
+        "node": ">=12.0.0"
+      },
+      "peerDependencies": {
+        "picomatch": "^3 || ^4"
+      },
+      "peerDependenciesMeta": {
+        "picomatch": {
+          "optional": true
+        }
+      }
+    },
+    "node_modules/vite-node/node_modules/picomatch": {
+      "version": "4.0.3",
+      "resolved": "https://registry.npmjs.org/picomatch/-/picomatch-4.0.3.tgz",
+      "integrity": "sha512-5gTmgEY/sqK6gFXLIsQNH19lWb4ebPDLA4SdLP7dsWkIXHWlG66oPuVvXSGFPppYZz8ZDZq0dYYrbHfBCVUb1Q==",
+      "dev": true,
+      "license": "MIT",
+      "engines": {
+        "node": ">=12"
+      },
+      "funding": {
+        "url": "https://github.com/sponsors/jonschlinkert"
+      }
+    },
+    "node_modules/vite-node/node_modules/rollup": {
+      "version": "4.52.2",
+      "resolved": "https://registry.npmjs.org/rollup/-/rollup-4.52.2.tgz",
+      "integrity": "sha512-I25/2QgoROE1vYV+NQ1En9T9UFB9Cmfm2CJ83zZOlaDpvz29wGQSZXWKw7MiNXau7wYgB/T9fVIdIuEQ+KbiiA==",
+      "dev": true,
+      "license": "MIT",
+      "dependencies": {
+        "@types/estree": "1.0.8"
+      },
+      "bin": {
+        "rollup": "dist/bin/rollup"
+      },
+      "engines": {
         "node": ">=18.0.0",
         "npm": ">=8.0.0"
       },
@@ -22523,178 +22843,603 @@
         "fsevents": "~2.3.2"
       }
     },
-    "node_modules/vite-node/node_modules/tinyglobby": {
-      "version": "0.2.15",
-      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.15.tgz",
-      "integrity": "sha512-j2Zq4NyQYG5XMST4cbs02Ak8iJUdxRM0XI5QyxXuZOzKOINmWurp3smXu3y5wDcJrptwpSjgXHzIQxR0omXljQ==",
+    "node_modules/vite-node/node_modules/tinyglobby": {
+      "version": "0.2.15",
+      "resolved": "https://registry.npmjs.org/tinyglobby/-/tinyglobby-0.2.15.tgz",
+      "integrity": "sha512-j2Zq4NyQYG5XMST4cbs02Ak8iJUdxRM0XI5QyxXuZOzKOINmWurp3smXu3y5wDcJrptwpSjgXHzIQxR0omXljQ==",
+      "dev": true,
+      "license": "MIT",
+      "dependencies": {
+        "fdir": "^6.5.0",
+        "picomatch": "^4.0.3"
+      },
+      "engines": {
+        "node": ">=12.0.0"
+      },
+      "funding": {
+        "url": "https://github.com/sponsors/SuperchupuDev"
+      }
+    },
+    "node_modules/vite-node/node_modules/undici-types": {
+      "version": "7.12.0",
+      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-7.12.0.tgz",
+      "integrity": "sha512-goOacqME2GYyOZZfb5Lgtu+1IDmAlAEu5xnD3+xTzS10hT0vzpf0SPjkXwAw9Jm+4n/mQGDP3LO8CPbYROeBfQ==",
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "peer": true
+    },
+    "node_modules/vite-node/node_modules/vite": {
+      "version": "7.3.1",
+      "resolved": "https://registry.npmjs.org/vite/-/vite-7.3.1.tgz",
+      "integrity": "sha512-w+N7Hifpc3gRjZ63vYBXA56dvvRlNWRczTdmCBBa+CotUzAPf5b7YMdMR/8CQoeYE5LX3W4wj6RYTgonm1b9DA==",
+      "dev": true,
+      "license": "MIT",
+      "dependencies": {
+        "esbuild": "^0.27.0",
+        "fdir": "^6.5.0",
+        "picomatch": "^4.0.3",
+        "postcss": "^8.5.6",
+        "rollup": "^4.43.0",
+        "tinyglobby": "^0.2.15"
+      },
+      "bin": {
+        "vite": "bin/vite.js"
+      },
+      "engines": {
+        "node": "^20.19.0 || >=22.12.0"
+      },
+      "funding": {
+        "url": "https://github.com/vitejs/vite?sponsor=1"
+      },
+      "optionalDependencies": {
+        "fsevents": "~2.3.3"
+      },
+      "peerDependencies": {
+        "@types/node": "^20.19.0 || >=22.12.0",
+        "jiti": ">=1.21.0",
+        "less": "^4.0.0",
+        "lightningcss": "^1.21.0",
+        "sass": "^1.70.0",
+        "sass-embedded": "^1.70.0",
+        "stylus": ">=0.54.8",
+        "sugarss": "^5.0.0",
+        "terser": "^5.16.0",
+        "tsx": "^4.8.1",
+        "yaml": "^2.4.2"
+      },
+      "peerDependenciesMeta": {
+        "@types/node": {
+          "optional": true
+        },
+        "jiti": {
+          "optional": true
+        },
+        "less": {
+          "optional": true
+        },
+        "lightningcss": {
+          "optional": true
+        },
+        "sass": {
+          "optional": true
+        },
+        "sass-embedded": {
+          "optional": true
+        },
+        "stylus": {
+          "optional": true
+        },
+        "sugarss": {
+          "optional": true
+        },
+        "terser": {
+          "optional": true
+        },
+        "tsx": {
+          "optional": true
+        },
+        "yaml": {
+          "optional": true
+        }
+      }
+    },
+    "node_modules/vitest": {
+      "version": "3.2.4",
+      "resolved": "https://registry.npmjs.org/vitest/-/vitest-3.2.4.tgz",
+      "integrity": "sha512-LUCP5ev3GURDysTWiP47wRRUpLKMOfPh+yKTx3kVIEiu5KOMeqzpnYNsKyOoVrULivR8tLcks4+lga33Whn90A==",
+      "dev": true,
+      "license": "MIT",
+      "dependencies": {
+        "@types/chai": "^5.2.2",
+        "@vitest/expect": "3.2.4",
+        "@vitest/mocker": "3.2.4",
+        "@vitest/pretty-format": "^3.2.4",
+        "@vitest/runner": "3.2.4",
+        "@vitest/snapshot": "3.2.4",
+        "@vitest/spy": "3.2.4",
+        "@vitest/utils": "3.2.4",
+        "chai": "^5.2.0",
+        "debug": "^4.4.1",
+        "expect-type": "^1.2.1",
+        "magic-string": "^0.30.17",
+        "pathe": "^2.0.3",
+        "picomatch": "^4.0.2",
+        "std-env": "^3.9.0",
+        "tinybench": "^2.9.0",
+        "tinyexec": "^0.3.2",
+        "tinyglobby": "^0.2.14",
+        "tinypool": "^1.1.1",
+        "tinyrainbow": "^2.0.0",
+        "vite": "^5.0.0 || ^6.0.0 || ^7.0.0-0",
+        "vite-node": "3.2.4",
+        "why-is-node-running": "^2.3.0"
+      },
+      "bin": {
+        "vitest": "vitest.mjs"
+      },
+      "engines": {
+        "node": "^18.0.0 || ^20.0.0 || >=22.0.0"
+      },
+      "funding": {
+        "url": "https://opencollective.com/vitest"
+      },
+      "peerDependencies": {
+        "@edge-runtime/vm": "*",
+        "@types/debug": "^4.1.12",
+        "@types/node": "^18.0.0 || ^20.0.0 || >=22.0.0",
+        "@vitest/browser": "3.2.4",
+        "@vitest/ui": "3.2.4",
+        "happy-dom": "*",
+        "jsdom": "*"
+      },
+      "peerDependenciesMeta": {
+        "@edge-runtime/vm": {
+          "optional": true
+        },
+        "@types/debug": {
+          "optional": true
+        },
+        "@types/node": {
+          "optional": true
+        },
+        "@vitest/browser": {
+          "optional": true
+        },
+        "@vitest/ui": {
+          "optional": true
+        },
+        "happy-dom": {
+          "optional": true
+        },
+        "jsdom": {
+          "optional": true
+        }
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/aix-ppc64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/aix-ppc64/-/aix-ppc64-0.27.2.tgz",
+      "integrity": "sha512-GZMB+a0mOMZs4MpDbj8RJp4cw+w1WV5NYD6xzgvzUJ5Ek2jerwfO2eADyI6ExDSUED+1X8aMbegahsJi+8mgpw==",
+      "cpu": [
+        "ppc64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "aix"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/android-arm": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-arm/-/android-arm-0.27.2.tgz",
+      "integrity": "sha512-DVNI8jlPa7Ujbr1yjU2PfUSRtAUZPG9I1RwW4F4xFB1Imiu2on0ADiI/c3td+KmDtVKNbi+nffGDQMfcIMkwIA==",
+      "cpu": [
+        "arm"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "android"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/android-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-arm64/-/android-arm64-0.27.2.tgz",
+      "integrity": "sha512-pvz8ZZ7ot/RBphf8fv60ljmaoydPU12VuXHImtAs0XhLLw+EXBi2BLe3OYSBslR4rryHvweW5gmkKFwTiFy6KA==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "android"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/android-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/android-x64/-/android-x64-0.27.2.tgz",
+      "integrity": "sha512-z8Ank4Byh4TJJOh4wpz8g2vDy75zFL0TlZlkUkEwYXuPSgX8yzep596n6mT7905kA9uHZsf/o2OJZubl2l3M7A==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "android"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/darwin-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/darwin-arm64/-/darwin-arm64-0.27.2.tgz",
+      "integrity": "sha512-davCD2Zc80nzDVRwXTcQP/28fiJbcOwvdolL0sOiOsbwBa72kegmVU0Wrh1MYrbuCL98Omp5dVhQFWRKR2ZAlg==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "darwin"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/darwin-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/darwin-x64/-/darwin-x64-0.27.2.tgz",
+      "integrity": "sha512-ZxtijOmlQCBWGwbVmwOF/UCzuGIbUkqB1faQRf5akQmxRJ1ujusWsb3CVfk/9iZKr2L5SMU5wPBi1UWbvL+VQA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "darwin"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/freebsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/freebsd-arm64/-/freebsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-lS/9CN+rgqQ9czogxlMcBMGd+l8Q3Nj1MFQwBZJyoEKI50XGxwuzznYdwcav6lpOGv5BqaZXqvBSiB/kJ5op+g==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "freebsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/freebsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/freebsd-x64/-/freebsd-x64-0.27.2.tgz",
+      "integrity": "sha512-tAfqtNYb4YgPnJlEFu4c212HYjQWSO/w/h/lQaBK7RbwGIkBOuNKQI9tqWzx7Wtp7bTPaGC6MJvWI608P3wXYA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "freebsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-arm": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-arm/-/linux-arm-0.27.2.tgz",
+      "integrity": "sha512-vWfq4GaIMP9AIe4yj1ZUW18RDhx6EPQKjwe7n8BbIecFtCQG4CfHGaHuh7fdfq+y3LIA2vGS/o9ZBGVxIDi9hw==",
+      "cpu": [
+        "arm"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-arm64/-/linux-arm64-0.27.2.tgz",
+      "integrity": "sha512-hYxN8pr66NsCCiRFkHUAsxylNOcAQaxSSkHMMjcpx0si13t1LHFphxJZUiGwojB1a/Hd5OiPIqDdXONia6bhTw==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-ia32": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-ia32/-/linux-ia32-0.27.2.tgz",
+      "integrity": "sha512-MJt5BRRSScPDwG2hLelYhAAKh9imjHK5+NE/tvnRLbIqUWa+0E9N4WNMjmp/kXXPHZGqPLxggwVhz7QP8CTR8w==",
+      "cpu": [
+        "ia32"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-loong64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-loong64/-/linux-loong64-0.27.2.tgz",
+      "integrity": "sha512-lugyF1atnAT463aO6KPshVCJK5NgRnU4yb3FUumyVz+cGvZbontBgzeGFO1nF+dPueHD367a2ZXe1NtUkAjOtg==",
+      "cpu": [
+        "loong64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-mips64el": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-mips64el/-/linux-mips64el-0.27.2.tgz",
+      "integrity": "sha512-nlP2I6ArEBewvJ2gjrrkESEZkB5mIoaTswuqNFRv/WYd+ATtUpe9Y09RnJvgvdag7he0OWgEZWhviS1OTOKixw==",
+      "cpu": [
+        "mips64el"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-ppc64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-ppc64/-/linux-ppc64-0.27.2.tgz",
+      "integrity": "sha512-C92gnpey7tUQONqg1n6dKVbx3vphKtTHJaNG2Ok9lGwbZil6DrfyecMsp9CrmXGQJmZ7iiVXvvZH6Ml5hL6XdQ==",
+      "cpu": [
+        "ppc64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-riscv64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-riscv64/-/linux-riscv64-0.27.2.tgz",
+      "integrity": "sha512-B5BOmojNtUyN8AXlK0QJyvjEZkWwy/FKvakkTDCziX95AowLZKR6aCDhG7LeF7uMCXEJqwa8Bejz5LTPYm8AvA==",
+      "cpu": [
+        "riscv64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-s390x": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-s390x/-/linux-s390x-0.27.2.tgz",
+      "integrity": "sha512-p4bm9+wsPwup5Z8f4EpfN63qNagQ47Ua2znaqGH6bqLlmJ4bx97Y9JdqxgGZ6Y8xVTixUnEkoKSHcpRlDnNr5w==",
+      "cpu": [
+        "s390x"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/linux-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.27.2.tgz",
+      "integrity": "sha512-uwp2Tip5aPmH+NRUwTcfLb+W32WXjpFejTIOWZFw/v7/KnpCDKG66u4DLcurQpiYTiYwQ9B7KOeMJvLCu/OvbA==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "linux"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/netbsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/netbsd-arm64/-/netbsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-Kj6DiBlwXrPsCRDeRvGAUb/LNrBASrfqAIok+xB0LxK8CHqxZ037viF13ugfsIpePH93mX7xfJp97cyDuTZ3cw==",
+      "cpu": [
+        "arm64"
+      ],
       "dev": true,
       "license": "MIT",
-      "dependencies": {
-        "fdir": "^6.5.0",
-        "picomatch": "^4.0.3"
-      },
+      "optional": true,
+      "os": [
+        "netbsd"
+      ],
       "engines": {
-        "node": ">=12.0.0"
-      },
-      "funding": {
-        "url": "https://github.com/sponsors/SuperchupuDev"
+        "node": ">=18"
       }
     },
-    "node_modules/vite-node/node_modules/undici-types": {
-      "version": "7.12.0",
-      "resolved": "https://registry.npmjs.org/undici-types/-/undici-types-7.12.0.tgz",
-      "integrity": "sha512-goOacqME2GYyOZZfb5Lgtu+1IDmAlAEu5xnD3+xTzS10hT0vzpf0SPjkXwAw9Jm+4n/mQGDP3LO8CPbYROeBfQ==",
+    "node_modules/vitest/node_modules/@esbuild/netbsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/netbsd-x64/-/netbsd-x64-0.27.2.tgz",
+      "integrity": "sha512-HwGDZ0VLVBY3Y+Nw0JexZy9o/nUAWq9MlV7cahpaXKW6TOzfVno3y3/M8Ga8u8Yr7GldLOov27xiCnqRZf0tCA==",
+      "cpu": [
+        "x64"
+      ],
       "dev": true,
       "license": "MIT",
       "optional": true,
-      "peer": true
+      "os": [
+        "netbsd"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
     },
-    "node_modules/vite-node/node_modules/vite": {
-      "version": "7.1.7",
-      "resolved": "https://registry.npmjs.org/vite/-/vite-7.1.7.tgz",
-      "integrity": "sha512-VbA8ScMvAISJNJVbRDTJdCwqQoAareR/wutevKanhR2/1EkoXVZVkkORaYm/tNVCjP/UDTKtcw3bAkwOUdedmA==",
+    "node_modules/vitest/node_modules/@esbuild/openbsd-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/openbsd-arm64/-/openbsd-arm64-0.27.2.tgz",
+      "integrity": "sha512-DNIHH2BPQ5551A7oSHD0CKbwIA/Ox7+78/AWkbS5QoRzaqlev2uFayfSxq68EkonB+IKjiuxBFoV8ESJy8bOHA==",
+      "cpu": [
+        "arm64"
+      ],
       "dev": true,
       "license": "MIT",
-      "dependencies": {
-        "esbuild": "^0.25.0",
-        "fdir": "^6.5.0",
-        "picomatch": "^4.0.3",
-        "postcss": "^8.5.6",
-        "rollup": "^4.43.0",
-        "tinyglobby": "^0.2.15"
-      },
-      "bin": {
-        "vite": "bin/vite.js"
-      },
+      "optional": true,
+      "os": [
+        "openbsd"
+      ],
       "engines": {
-        "node": "^20.19.0 || >=22.12.0"
-      },
-      "funding": {
-        "url": "https://github.com/vitejs/vite?sponsor=1"
-      },
-      "optionalDependencies": {
-        "fsevents": "~2.3.3"
-      },
-      "peerDependencies": {
-        "@types/node": "^20.19.0 || >=22.12.0",
-        "jiti": ">=1.21.0",
-        "less": "^4.0.0",
-        "lightningcss": "^1.21.0",
-        "sass": "^1.70.0",
-        "sass-embedded": "^1.70.0",
-        "stylus": ">=0.54.8",
-        "sugarss": "^5.0.0",
-        "terser": "^5.16.0",
-        "tsx": "^4.8.1",
-        "yaml": "^2.4.2"
-      },
-      "peerDependenciesMeta": {
-        "@types/node": {
-          "optional": true
-        },
-        "jiti": {
-          "optional": true
-        },
-        "less": {
-          "optional": true
-        },
-        "lightningcss": {
-          "optional": true
-        },
-        "sass": {
-          "optional": true
-        },
-        "sass-embedded": {
-          "optional": true
-        },
-        "stylus": {
-          "optional": true
-        },
-        "sugarss": {
-          "optional": true
-        },
-        "terser": {
-          "optional": true
-        },
-        "tsx": {
-          "optional": true
-        },
-        "yaml": {
-          "optional": true
-        }
+        "node": ">=18"
       }
     },
-    "node_modules/vitest": {
-      "version": "3.2.4",
-      "resolved": "https://registry.npmjs.org/vitest/-/vitest-3.2.4.tgz",
-      "integrity": "sha512-LUCP5ev3GURDysTWiP47wRRUpLKMOfPh+yKTx3kVIEiu5KOMeqzpnYNsKyOoVrULivR8tLcks4+lga33Whn90A==",
+    "node_modules/vitest/node_modules/@esbuild/openbsd-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/openbsd-x64/-/openbsd-x64-0.27.2.tgz",
+      "integrity": "sha512-/it7w9Nb7+0KFIzjalNJVR5bOzA9Vay+yIPLVHfIQYG/j+j9VTH84aNB8ExGKPU4AzfaEvN9/V4HV+F+vo8OEg==",
+      "cpu": [
+        "x64"
+      ],
       "dev": true,
       "license": "MIT",
-      "dependencies": {
-        "@types/chai": "^5.2.2",
-        "@vitest/expect": "3.2.4",
-        "@vitest/mocker": "3.2.4",
-        "@vitest/pretty-format": "^3.2.4",
-        "@vitest/runner": "3.2.4",
-        "@vitest/snapshot": "3.2.4",
-        "@vitest/spy": "3.2.4",
-        "@vitest/utils": "3.2.4",
-        "chai": "^5.2.0",
-        "debug": "^4.4.1",
-        "expect-type": "^1.2.1",
-        "magic-string": "^0.30.17",
-        "pathe": "^2.0.3",
-        "picomatch": "^4.0.2",
-        "std-env": "^3.9.0",
-        "tinybench": "^2.9.0",
-        "tinyexec": "^0.3.2",
-        "tinyglobby": "^0.2.14",
-        "tinypool": "^1.1.1",
-        "tinyrainbow": "^2.0.0",
-        "vite": "^5.0.0 || ^6.0.0 || ^7.0.0-0",
-        "vite-node": "3.2.4",
-        "why-is-node-running": "^2.3.0"
-      },
-      "bin": {
-        "vitest": "vitest.mjs"
-      },
+      "optional": true,
+      "os": [
+        "openbsd"
+      ],
       "engines": {
-        "node": "^18.0.0 || ^20.0.0 || >=22.0.0"
-      },
-      "funding": {
-        "url": "https://opencollective.com/vitest"
-      },
-      "peerDependencies": {
-        "@edge-runtime/vm": "*",
-        "@types/debug": "^4.1.12",
-        "@types/node": "^18.0.0 || ^20.0.0 || >=22.0.0",
-        "@vitest/browser": "3.2.4",
-        "@vitest/ui": "3.2.4",
-        "happy-dom": "*",
-        "jsdom": "*"
-      },
-      "peerDependenciesMeta": {
-        "@edge-runtime/vm": {
-          "optional": true
-        },
-        "@types/debug": {
-          "optional": true
-        },
-        "@types/node": {
-          "optional": true
-        },
-        "@vitest/browser": {
-          "optional": true
-        },
-        "@vitest/ui": {
-          "optional": true
-        },
-        "happy-dom": {
-          "optional": true
-        },
-        "jsdom": {
-          "optional": true
-        }
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/sunos-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/sunos-x64/-/sunos-x64-0.27.2.tgz",
+      "integrity": "sha512-kMtx1yqJHTmqaqHPAzKCAkDaKsffmXkPHThSfRwZGyuqyIeBvf08KSsYXl+abf5HDAPMJIPnbBfXvP2ZC2TfHg==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "sunos"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/win32-arm64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-arm64/-/win32-arm64-0.27.2.tgz",
+      "integrity": "sha512-Yaf78O/B3Kkh+nKABUF++bvJv5Ijoy9AN1ww904rOXZFLWVc5OLOfL56W+C8F9xn5JQZa3UX6m+IktJnIb1Jjg==",
+      "cpu": [
+        "arm64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/win32-ia32": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-ia32/-/win32-ia32-0.27.2.tgz",
+      "integrity": "sha512-Iuws0kxo4yusk7sw70Xa2E2imZU5HoixzxfGCdxwBdhiDgt9vX9VUCBhqcwY7/uh//78A1hMkkROMJq9l27oLQ==",
+      "cpu": [
+        "ia32"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
+      }
+    },
+    "node_modules/vitest/node_modules/@esbuild/win32-x64": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/@esbuild/win32-x64/-/win32-x64-0.27.2.tgz",
+      "integrity": "sha512-sRdU18mcKf7F+YgheI/zGf5alZatMUTKj/jNS6l744f9u3WFu4v7twcUI9vu4mknF4Y9aDlblIie0IM+5xxaqQ==",
+      "cpu": [
+        "x64"
+      ],
+      "dev": true,
+      "license": "MIT",
+      "optional": true,
+      "os": [
+        "win32"
+      ],
+      "engines": {
+        "node": ">=18"
       }
     },
     "node_modules/vitest/node_modules/@types/estree": {
@@ -22731,6 +23476,48 @@
         }
       }
     },
+    "node_modules/vitest/node_modules/esbuild": {
+      "version": "0.27.2",
+      "resolved": "https://registry.npmjs.org/esbuild/-/esbuild-0.27.2.tgz",
+      "integrity": "sha512-HyNQImnsOC7X9PMNaCIeAm4ISCQXs5a5YasTXVliKv4uuBo1dKrG0A+uQS8M5eXjVMnLg3WgXaKvprHlFJQffw==",
+      "dev": true,
+      "hasInstallScript": true,
+      "license": "MIT",
+      "bin": {
+        "esbuild": "bin/esbuild"
+      },
+      "engines": {
+        "node": ">=18"
+      },
+      "optionalDependencies": {
+        "@esbuild/aix-ppc64": "0.27.2",
+        "@esbuild/android-arm": "0.27.2",
+        "@esbuild/android-arm64": "0.27.2",
+        "@esbuild/android-x64": "0.27.2",
+        "@esbuild/darwin-arm64": "0.27.2",
+        "@esbuild/darwin-x64": "0.27.2",
+        "@esbuild/freebsd-arm64": "0.27.2",
+        "@esbuild/freebsd-x64": "0.27.2",
+        "@esbuild/linux-arm": "0.27.2",
+        "@esbuild/linux-arm64": "0.27.2",
+        "@esbuild/linux-ia32": "0.27.2",
+        "@esbuild/linux-loong64": "0.27.2",
+        "@esbuild/linux-mips64el": "0.27.2",
+        "@esbuild/linux-ppc64": "0.27.2",
+        "@esbuild/linux-riscv64": "0.27.2",
+        "@esbuild/linux-s390x": "0.27.2",
+        "@esbuild/linux-x64": "0.27.2",
+        "@esbuild/netbsd-arm64": "0.27.2",
+        "@esbuild/netbsd-x64": "0.27.2",
+        "@esbuild/openbsd-arm64": "0.27.2",
+        "@esbuild/openbsd-x64": "0.27.2",
+        "@esbuild/openharmony-arm64": "0.27.2",
+        "@esbuild/sunos-x64": "0.27.2",
+        "@esbuild/win32-arm64": "0.27.2",
+        "@esbuild/win32-ia32": "0.27.2",
+        "@esbuild/win32-x64": "0.27.2"
+      }
+    },
     "node_modules/vitest/node_modules/estree-walker": {
       "version": "3.0.3",
       "resolved": "https://registry.npmjs.org/estree-walker/-/estree-walker-3.0.3.tgz",
@@ -22842,13 +23629,13 @@
       }
     },
     "node_modules/vitest/node_modules/vite": {
-      "version": "7.1.7",
-      "resolved": "https://registry.npmjs.org/vite/-/vite-7.1.7.tgz",
-      "integrity": "sha512-VbA8ScMvAISJNJVbRDTJdCwqQoAareR/wutevKanhR2/1EkoXVZVkkORaYm/tNVCjP/UDTKtcw3bAkwOUdedmA==",
+      "version": "7.3.1",
+      "resolved": "https://registry.npmjs.org/vite/-/vite-7.3.1.tgz",
+      "integrity": "sha512-w+N7Hifpc3gRjZ63vYBXA56dvvRlNWRczTdmCBBa+CotUzAPf5b7YMdMR/8CQoeYE5LX3W4wj6RYTgonm1b9DA==",
       "dev": true,
       "license": "MIT",
       "dependencies": {
-        "esbuild": "^0.25.0",
+        "esbuild": "^0.27.0",
         "fdir": "^6.5.0",
         "picomatch": "^4.0.3",
         "postcss": "^8.5.6",
```

### package.json
```diff
@@ -55,6 +55,11 @@
   "bugs": {
     "url": "https://github.com/walletconnect/walletconnect-monorepo/issues"
   },
+  "overrides": {
+    "tar": "^7.5.7",
+    "lodash": "^4.17.23",
+    "vite": "^7.3.1"
+  },
   "devDependencies": {
     "@changesets/changelog-github": "0.5.2",
     "@changesets/cli": "2.29.8",
```
