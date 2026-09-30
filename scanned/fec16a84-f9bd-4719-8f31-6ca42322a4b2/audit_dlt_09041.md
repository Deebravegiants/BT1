# [?] release(cp): chore: fix newly reported dependency audit vulnerabilities by updating minimatch-related deps (#40315)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-27
Source: https://github.com/MetaMask/metamask-extension/commit/497b7ee32cfc4ec18d7b66fe384772455691c420
Type: security-commit

## Details
release(cp): chore: fix newly reported dependency audit vulnerabilities by updating minimatch-related deps (#40315)

## Patch
### .eslintrc.js
```diff
@@ -588,7 +588,7 @@ module.exports = {
       files: ['development/**/*.js', 'test/helpers/setup-helper.js'],
       rules: {
         'n/no-process-exit': 'off',
-        'n/shebang': 'off',
+        'n/hashbang': 'off',
       },
     },
     /**
```

### .eslintrc.node.js
```diff
@@ -2,6 +2,16 @@ module.exports = {
   extends: ['@metamask/eslint-config-nodejs'],
   rules: {
     'n/no-process-env': 'off',
+    // eslint-plugin-n@17 started treating these browser globals as Node builtins
+    // and `n/hashbang` started flagging existing script headers in this repo.
+    // Keep prior behavior while we remain on the current shared config stack.
+    'n/no-unsupported-features/node-builtins': [
+      'error',
+      {
+        ignores: ['navigator', 'Navigator', 'localStorage'],
+      },
+    ],
+    'n/hashbang': 'off',
     // TODO: re-enable these rules
     'n/no-sync': 'off',
     'n/no-unpublished-import': 'off',
```

### .yarnrc.yml
```diff
@@ -26,29 +26,6 @@ npmAuditIgnoreAdvisories:
   # We are ignoring this on April 24, 2025 to unblock CI, we will follow with a proper fix or confirmation this does not affect our users
   - 1104001
 
-  # Issue: `glob` vulnerability, already fixed in the version we're using (v10.5.0) but the
-  # advisory range hasn't been updated yet.
-  # URL: https://github.com/advisories/GHSA-5j98-mcp5-4vw2
-  - 1109809
-
-  # Issue: `body-parser` denial of service vulnerability
-  # Seemingly only impacts v2.2.0, but we're on v1. The advisory range is overly wide.
-  # The attack vector also does not apply to how we use the package.
-  # URL: https://github.com/advisories/GHSA-wqch-xfxh-vrr4
-  - 1110857
-
-  # Issue: ajv has ReDoS when using `$data` option
-  # A lot of our linting tooling relies on old versions of ajv, which proves hard to deal with
-  # For now, we are ignoring this to unblock CI
-  # URL: https://github.com/advisories/GHSA-2g4f-4pwh-qvx6
-  - 1113214
-
-  # Issue: minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern
-  # Only affects dev/build-time dependencies (eslint-plugin-n, glob) — not shipped to users.
-  # URL: https://github.com/advisories/GHSA-3ppc-4f35-3m26
-  - 1113371
-  - 1113459
-
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
@@ -104,3 +81,5 @@ npmPreapprovedPackages:
   - 'lavamoat-node'
   - 'lavamoat'
   - 'extension-port-stream'
+  # Temporary bypass for recent minimatch security patch; remove once older than age gate.
+  - 'minimatch'
```

### attribution.txt
```diff
@@ -2509,33 +2509,6 @@ TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 
 
-******************************
-
-balanced-match
-1.0.2 <https://github.com/juliangruber/balanced-match>
-(MIT)
-
-Copyright (c) 2013 Julian Gruber &lt;julian@juliangruber.com&gt;
-
-Permission is hereby granted, free of charge, to any person obtaining a copy of
-this software and associated documentation files (the "Software"), to deal in
-the Software without restriction, including without limitation the rights to
-use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
-of the Software, and to permit persons to whom the Software is furnished to do
-so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all
-copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-SOFTWARE.
-
-
 ******************************
 
 bare-addon-resolve
@@ -4662,33 +4635,6 @@ programs and associated documentation files created by the
 Original Author, when distributed with the Software.
 
 
-******************************
-
-brace-expansion
-1.1.11 <https://github.com/juliangruber/brace-expansion>
-MIT License
-
-Copyright (c) 2013 Julian Gruber <julian@juliangruber.com>
-
-Permission is hereby granted, free of charge, to any person obtaining a copy
-of this software and associated documentation files (the "Software"), to deal
-in the Software without restriction, including without limitation the rights
-to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-copies of the Software, and to permit persons to whom the Software is
-furnished to do so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all
-copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
-SOFTWARE.
-
-
 ******************************
 
 braces
@@ -4999,21 +4945,6 @@ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 
 
-******************************
-
-builtin-modules
-3.3.0 <https://github.com/sindresorhus/builtin-modules>
-MIT License
-
-Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https://sindresorhus.com)
-
-Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-
-
 ******************************
 
 builtins
@@ -6306,30 +6237,6 @@ component-type
 license: MIT
 authors: undefined
 
-******************************
-
-concat-map
-0.0.1 <https://github.com/substack/node-concat-map>
-This software is released under the MIT license:
-
-Permission is hereby granted, free of charge, to any person obtaining a copy of
-this software and associated documentation files (the "Software"), to deal in
-the Software without restriction, including without limitation the rights to
-use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
-the Software, and to permit persons to whom the Software is furnished to do so,
-subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all
-copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
-FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
-COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
-IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
-CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-
-
 ******************************
 
 concat-stream
@@ -13737,6 +13644,32 @@ THE SOFTWARE.
    limitations under the License.
 
 
+******************************
+
+enhanced-resolve
+5.19.0 <https://github.com/webpack/enhanced-resolve>
+Copyright JS Foundation and other contributors
+
+Permission is hereby granted, free of charge, to any person obtaining
+a copy of this software and associated documentation files (the
+'Software'), to deal in the Software without restriction, including
+without limitation the rights to use, copy, modify, merge, publish,
+distribute, sublicense, and/or sell copies of the Software, and to
+permit persons to whom the Software is furnished to do so, subject to
+the following conditions:
+
+The above copyright notice and this permission notice shall be
+included in all copies or substantial portions of the Software.
+
+THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND,
+EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
+MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
+IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
+CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
+TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
+SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
+
+
 ******************************
 
 @ensdomains/content-hash
@@ -13940,7 +13873,7 @@ SOFTWARE.
 ******************************
 
 eslint-compat-utils
-0.1.2 <https://github.com/ota-meshi/eslint-compat-utils>
+0.5.1 <https://github.com/ota-meshi/eslint-compat-utils>
 MIT License
 
 Copyright (c) 2023 Yosuke Ota
@@ -13967,7 +13900,7 @@ SOFTWARE.
 ******************************
 
 eslint-plugin-es-x
-7.5.0 <https://github.com/eslint-community/eslint-plugin-es-x>
+7.8.0 <https://github.com/eslint-community/eslint-plugin-es-x>
 MIT License
 
 Copyright (c) 2018 Toru Nagashima
@@ -13994,7 +13927,7 @@ SOFTWARE.
 ******************************
 
 eslint-plugin-n
-16.6.2 <https://github.com/eslint-community/eslint-plugin-n>
+17.24.0 <https://github.com/eslint-community/eslint-plugin-n>
 The MIT License (MIT)
 
 Copyright (c) 2015 Toru Nagashima
@@ -20115,7 +20048,7 @@ THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLI
 ******************************
 
 globals
-13.24.0 <https://github.com/sindresorhus/globals>
+15.15.0 <https://github.com/sindresorhus/globals>
 MIT License
 
 Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https://sindresorhus.com)
@@ -20148,6 +20081,33 @@ ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
 IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
 
 
+******************************
+
+globrex
+0.1.2 <https://github.com/terkelg/globrex>
+MIT License
+
+Copyright (c) 2018 Terkel Gjervig Nielsen
+
+Permission is hereby granted, free of charge, to any person obtaining a copy
+of this software and associated documentation files (the "Software"), to deal
+in the Software without restriction, including without limitation the rights
+to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+copies of the Software, and to permit persons to whom the Software is
+furnished to do so, subject to the following conditions:
+
+The above copyright notice and this permission notice shall be included in all
+copies or substantial portions of the Software.
+
+THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
+AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
+SOFTWARE.
+
+
 ******************************
 
 gl-vec3
@@ -21736,21 +21696,6 @@ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
 
 
-******************************
-
-is-builtin-module
-3.2.1 <https://github.com/sindresorhus/is-builtin-module>
-MIT License
-
-Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (sindresorhus.com)
-
-Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-
-
 ******************************
 
 is-callable
@@ -35253,27 +35198,6 @@ minimalistic-crypto-utils
 license: MIT
 authors: Fedor Indutny <fedor@indutny.com>
 
-******************************
-
-minimatch
-3.1.2 <https://github.com/isaacs/minimatch>
-The ISC License
-
-Copyright (c) Isaac Z. Schlueter and Contributors
-
-Permission to use, copy, modify, and/or distribute this software for any
-purpose with or without fee is hereby granted, provided that the above
-copyright notice and this permission notice appear in all copies.
-
-THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
-WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
-MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
-ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
-WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
-ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR
-IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
-
-
 ******************************
 
 minimist
@@ -45881,6 +45805,33 @@ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 
 
+******************************
+
+tapable
+2.3.0 <https://github.com/webpack/tapable>
+The MIT License
+
+Copyright JS Foundation and other contributors
+
+Permission is hereby granted, free of charge, to any person obtaining a copy
+of this software and associated documentation files (the "Software"), to deal
+in the Software without restriction, including without limitation the rights
+to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
+copies of the Software, and to permit persons to whom the Software is
+furnished to do so, subject to the following conditions:
+
+The above copyright notice and this permission notice shall be included in
+all copies or substantial portions of the Software.
+
+THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
+IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
+FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
+AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
+LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
+OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
+THE SOFTWARE.
+
+
 ******************************
 
 tar-fs
@@ -47051,6 +47002,41 @@ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
 
 
+******************************
+
+ts-declaration-location
+1.0.7 <https://github.com/RebeccaStevens/ts-declaration-location>
+BSD 3-Clause License
+
+Copyright (c) 2023, Rebecca Stevens
+All rights reserved.
+
+Redistribution and use in source and binary forms, with or without
+modification, are permitted provided that the following conditions are met:
+
+1. Redistributions of source code must retain the above copyright notice, this
+   list of conditions and the following disclaimer.
+
+2. Redistributions in binary form must reproduce the above copyright notice,
+   this list of conditions and the following disclaimer in the documentation
+   and/or other materials provided with the distribution.
+
+3. Neither the name of the copyright holder nor the names of its
+   contributors may be used to endorse or promote products derived from
+   this software without specific prior written permission.
+
+THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
+AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
+IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
+DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
+FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
+DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
+SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
+CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
+OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
+OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
+
+
 ******************************
 
 ts-interface-checker
@@ -47460,21 +47446,6 @@ OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
 
 
-******************************
-
-type-fest
-0.20.2 <https://github.com/sindresorhus/type-fest>
-MIT License
-
-Copyright (c) Sindre Sorhus <sindresorhus@gmail.com> (https:/sindresorhus.com)
-
-Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
-
-The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
-
-THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-
-
 ******************************
 
 type-fest
```

### lavamoat/browserify/beta/policy.json
```diff
@@ -3877,7 +3877,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6433,7 +6433,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```

### lavamoat/browserify/experimental/policy.json
```diff
@@ -3877,7 +3877,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6433,7 +6433,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```

### lavamoat/browserify/flask/policy.json
```diff
@@ -3877,7 +3877,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6433,7 +6433,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```

### lavamoat/browserify/main/policy.json
```diff
@@ -3877,7 +3877,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6433,7 +6433,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```

### lavamoat/build-system/policy.json
```diff
@@ -806,7 +806,7 @@
         "@babel/core>@babel/template": true,
         "lavamoat>lavamoat-tofu>@babel/traverse>@babel/types": true,
         "nock>debug": true,
-        "lavamoat>lavamoat-tofu>@babel/traverse>globals": true
+        "@babel/preset-env>@babel/plugin-transform-classes>globals": true
       }
     },
     "@babel/core>@babel/types": {
@@ -905,7 +905,7 @@
         "eslint-plugin-prettier": true,
         "eslint-plugin-react": true,
         "eslint-plugin-react-hooks": true,
-        "eslint>globals": true,
+        "eslint>@eslint/eslintrc>globals": true,
         "eslint>ignore": true,
         "eslint>minimatch": true,
         "mocha>strip-json-comments": true
@@ -1781,14 +1781,6 @@
         "Buffer": true
       }
     },
-    "eslint-plugin-n>builtins": {
-      "globals": {
-        "process.version": true
-      },
-      "packages": {
-        "semver": true
-      }
-    },
     "gulp>gulp-cli>matchdep>micromatch>snapdragon>base>cache-base": {
       "packages": {
         "gulp>gulp-cli>matchdep>micromatch>snapdragon>base>cache-base>collection-visit": true,
@@ -2526,6 +2518,30 @@
         "@metamask/object-multiplex>once": true
       }
     },
+    "webpack>enhanced-resolve": {
+      "builtin": {
+        "module.findPnpApi": true,
+        "path.basename": true,
+        "path.posix.dirname": true,
+        "path.posix.normalize": true,
+        "path.win32.dirname": true,
+        "path.win32.normalize": true,
+        "process.nextTick": true,
+        "process.versions.pnp": true,
+        "url": true
+      },
+      "globals": {
+        "Buffer.isBuffer": true,
+        "URL": true,
+        "clearTimeout": true,
+        "process.cwd": true,
+        "setTimeout": true
+      },
+      "packages": {
+        "del>graceful-fs": true,
+        "webpack>tapable": true
+      }
+    },
     "gulp-livereload>tiny-lr>body>error": {
       "builtin": {
         "assert": true
@@ -2708,6 +2724,17 @@
         "eslint>natural-compare": true
       }
     },
+    "eslint-plugin-n>eslint-plugin-es-x>eslint-compat-utils": {
+      "builtin": {
+        "fs.existsSync": true,
+        "path.basename": true,
+        "path.dirname": true,
+        "path.extname": true
+      },
+      "globals": {
+        "process.cwd": true
+      }
+    },
     "eslint-config-prettier": {
       "globals": {
         "process.env.ESLINT_CONFIG_PRETTIER_NO_DEPRECATED": true
@@ -2766,13 +2793,14 @@
         "eslint-import-resolver-node": true
       }
     },
-    "eslint-plugin-n>eslint-plugin-es": {
+    "eslint-plugin-n>eslint-plugin-es-x": {
       "globals": {
         "process": true
       },
       "packages": {
-        "eslint-plugin-n>eslint-plugin-es>eslint-utils": true,
-        "eslint-plugin-n>eslint-plugin-es>regexpp": true
+        "eslint>@eslint-community/eslint-utils": true,
+        "eslint>@eslint-community/regexpp": true,
+        "eslint-plugin-n>eslint-plugin-es-x>eslint-compat-utils": true
       }
     },
     "eslint-plugin-import": {
@@ -2839,29 +2867,34 @@
     },
     "eslint-plugin-n": {
       "builtin": {
-        "assert": true,
-        "fs": true,
-        "path": true,
-        "url.URL": true,
-        "url.fileURLToPath": true,
-        "url.pathToFileURL": true,
-        "util.format": true,
-        "util.inspect": true
+        "fs.existsSync": true,
+        "fs.readFileSync": true,
+        "fs.readdirSync": true,
+        "fs.statSync": true,
+        "node:module.isBuiltin": true,
+        "path.basename": true,
+        "path.dirname": true,
+        "path.extname": true,
+        "path.isAbsolute": true,
+        "path.join": true,
+        "path.posix.normalize": true,
+        "path.relative": true,
+        "path.resolve": true,
+        "path.sep": true
       },
       "globals": {
-        "process.cwd": true,
-        "process.emitWarning": true,
-        "process.platform": true
+        "process.cwd": true
       },
       "packages": {
-        "eslint-plugin-n>builtins": true,
-        "eslint-plugin-n>eslint-plugin-es": true,
-        "eslint-plugin-n>eslint-utils": true,
+        "eslint>@eslint-community/eslint-utils": true,
+        "webpack>enhanced-resolve": true,
+        "eslint-plugin-n>eslint-plugin-es-x": true,
+        "tsx>get-tsconfig": true,
+        "eslint-plugin-n>globals": true,
+        "eslint-plugin-n>globrex": true,
         "eslint>ignore": true,
-        "depcheck>is-core-module": true,
-        "eslint>minimatch": true,
-        "depcheck>resolve": true,
-        "semver": true
+        "semver": true,
+        "typescript": true
       }
     },
     "eslint-plugin-prettier": {
@@ -2940,21 +2973,11 @@
         "semver": true
       }
     },
-    "eslint-plugin-n>eslint-plugin-es>eslint-utils": {
-      "packages": {
-        "eslint-plugin-n>eslint-plugin-es>eslint-utils>eslint-visitor-keys": true
-      }
-    },
     "eslint-plugin-mocha>eslint-utils": {
       "packages": {
         "eslint-plugin-mocha>eslint-utils>eslint-visitor-keys": true
       }
     },
-    "eslint-plugin-n>eslint-utils": {
-      "packages": {
-        "eslint-plugin-n>eslint-utils>eslint-visitor-keys": true
-      }
-    },
     "eslint>espree": {
       "packages": {
         "eslint>espree>acorn-jsx": true,
@@ -3495,6 +3518,29 @@
         "pumpify>pump": true
       }
     },
+    "tsx>get-tsconfig": {
+      "builtin": {
+        "fs": true,
+        "node:fs": true,
+        "node:module": true,
+        "node:path.dirname": true,
+        "node:path.isAbsolute": true,
+        "node:path.join": true,
+        "node:path.posix": true,
+        "node:path.relative": true,
+        "node:path.resolve": true,
+        "os.tmpdir": true,
+        "path.join": true
+      },
+      "globals": {
+        "process.cwd": true,
+        "process.pid": true,
+        "process.platform": true
+      },
+      "packages": {
+        "tsx>get-tsconfig>resolve-pkg-maps": true
+      }
+    },
     "gulp-watch>anymatch>micromatch>parse-glob>glob-base": {
       "builtin": {
         "path.dirname": true
@@ -3600,6 +3646,11 @@
         "del>slash": true
       }
     },
+    "eslint-plugin-n>globrex": {
+      "globals": {
+        "process.platform": true
+      }
+    },
     "del>graceful-fs": {
       "builtin": {
         "assert.equal": true,
@@ -7204,6 +7255,11 @@
         "tailwindcss>sucrase": true
       }
     },
+    "webpack>tapable": {
+      "builtin": {
+        "util.deprecate": true
+      }
+    },
     "terser": {
       "globals": {
         "Buffer": true,
```

### lavamoat/webpack/build/policy-override.json
```diff
@@ -12,6 +12,19 @@
       },
       "native": true
     },
+    "copy-webpack-plugin": {
+      "packages": {
+        "copy-webpack-plugin>serialize-javascript": true
+      }
+    },
+    "copy-webpack-plugin>serialize-javascript": {
+      "globals": {
+        "URL": true
+      },
+      "packages": {
+        "crypto-browserify>randombytes": true
+      }
+    },
     "@swc/core": {
       "packages": {
         "@swc/core>@swc/core-darwin-x64": true,
```

### lavamoat/webpack/build/policy.json
```diff
@@ -236,7 +236,7 @@
         "@babel/core>@babel/template": true,
         "lavamoat>lavamoat-tofu>@babel/traverse>@babel/types": true,
         "nock>debug": true,
-        "lavamoat>lavamoat-tofu>@babel/traverse>globals": true
+        "@babel/preset-env>@babel/plugin-transform-classes>globals": true
       }
     },
     "@babel/core>@babel/types": {
@@ -1336,7 +1336,9 @@
       "builtin": {
         "module.findPnpApi": true,
         "path.basename": true,
+        "path.posix.dirname": true,
         "path.posix.normalize": true,
+        "path.win32.dirname": true,
         "path.win32.normalize": true,
         "process.nextTick": true,
         "process.versions.pnp": true,
@@ -1346,6 +1348,7 @@
         "Buffer.isBuffer": true,
         "URL": true,
         "clearTimeout": true,
+        "process.cwd": true,
         "setTimeout": true
       },
       "packages": {
```

### lavamoat/webpack/mv2/beta/policy.json
```diff
@@ -3688,7 +3688,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "globals": {
         "process.version": true
       },
@@ -6421,7 +6421,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```
