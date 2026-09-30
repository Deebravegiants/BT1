# [?] chore: fix newly reported dependency audit vulnerabilities by updating minimatch-related deps (#40315)

## Summary
Severity: Unknown
Chain: MetaMask
Component: MetaMask/metamask-extension
Published: 2026-02-27
Source: https://github.com/MetaMask/metamask-extension/commit/37331b596a220bd0e216449e0aa0d682aa3035b5
Type: security-commit

## Details
chore: fix newly reported dependency audit vulnerabilities by updating minimatch-related deps (#40315)

## **Description**

This PR fixes dependency audit vulnerabilities and keeps the fixes
durable in dependency resolution.

What changed:
- Added/updated Yarn `resolutions` to enforce patched versions for
vulnerable paths:
  - `minimatch@npm:^10.1.1` -> `10.2.1`
  - `bn.js` -> `5.2.3`
  - `ajv` v6 path -> `6.14.0`
  - `ajv` v8 paths -> `8.18.0`
- Updated root `eslint-plugin-n` to `^17.24.0`.
- Added ESLint compatibility overrides (`.eslintrc.base.js`,
`.eslintrc.node.js`) to preserve existing lint behavior after the
`eslint-plugin-n` upgrade.
- Removed stale Yarn `npmAuditIgnoreAdvisories` entries for advisories
now resolved in this branch:
  - `1113214` (ajv)
  - `1113296` (minimatch).

Why:
- CI/dependency audit reported vulnerable transitive dependency paths
that need explicit, durable pinning.
- Upgrading `eslint-plugin-n` was required to eliminate one flagged
vulnerable path, and the ESLint overrides were needed to keep lint
checks passing with existing browser/runtime code patterns.

## **Changelog**

CHANGELOG entry: null

<!--
## **Related issues**

Fixes:
-->

<!--
## **Screenshots/Recordings**

### **Before**

[screenshots/recordings]

### **After**

[screenshots/recordings]
-->

## **Pre-merge author checklist**

- [ ] I've followed [MetaMask Contributor
Docs](https://github.com/MetaMask/contributor-docs) and [MetaMask
Extension Coding
Standards](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/CODING_GUIDELINES.md).
- [ ] I've completed the PR template to the best of my ability
- [ ] I’ve included tests if applicable
- [ ] I’ve documented my code using [JSDoc](https://jsdoc.app/) format
if applicable
- [ ] I’ve applied the right labels on the PR (see [labeling
guidelines](https://github.com/MetaMask/metamask-extension/blob/main/.github/guidelines/LABELING_GUIDELINES.md)).
Not required for external contributors.

## **Pre-merge reviewer checklist**

- [ ] I've manually tested the PR (e.g. pull and build branch, run the
app, test code being changed).
- [ ] I confirm that this PR addresses all acceptance criteria described
in the ticket it closes and includes the necessary testing evidence such
as recordings and or screenshots.

[skip-e2e]

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Medium Risk**
> Touches dependency resolution and LavaMoat policies plus tweaks ESLint
rules; main risk is CI/build/lint breakage due to changed transitive
deps and updated allowlists, but no runtime product logic changes.
> 
> **Overview**
> Updates dependency pinning to address audit findings: bumps
`minimatch` (via `resolutions`) and `bn.js`, and upgrades
`eslint-plugin-n` to `^17.24.0` with updated `yarn.lock` entries.
> 
> Adjusts ESLint configuration for the `eslint-plugin-n` v17 rule
changes (rename `n/shebang` -> `n/hashbang`, disables `n/hashbang`, and
adds `n/no-unsupported-features/node-builtins` ignores for browser
globals), and updates related test helper lint disables.
> 
> Refreshes LavaMoat policies/overrides to match the new dependency
graph (new/renamed policy nodes and additional allowed
builtins/packages, including `webpack`/`tsx`/`copy-webpack-plugin`
related entries), and removes an obsolete `npmAuditIgnoreAdvisories`
entry while temporarily preapproving `minimatch` for the minimal-age
gate.
> 
> <sup>Written by [Cursor
Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit
02e3238a42103a59302dac89a7199f919a07190e. This will update automatically
on new commits. Configure
[here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

---------

Co-authored-by: MetaMask Bot <metamaskbot@users.noreply.github.com>

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
@@ -26,11 +26,6 @@ npmAuditIgnoreAdvisories:
   # We are ignoring this on April 24, 2025 to unblock CI, we will follow with a proper fix or confirmation this does not affect our users
   - 1104001
 
-  # Issue: minimatch has a ReDoS via repeated wildcards with non-matching literal in pattern
-  # Only affects dev/build-time dependencies (eslint-plugin-n, glob) — not shipped to users.
-  # URL: https://github.com/advisories/GHSA-3ppc-4f35-3m26
-  - 1113459
-
   ### Package Deprecations:
 
   # React-tippy brings in popper.js and react-tippy has not been updated in
@@ -86,3 +81,5 @@ npmPreapprovedPackages:
   - 'lavamoat-node'
   - 'lavamoat'
   - 'extension-port-stream'
+  # Temporary bypass for recent minimatch security patch; remove once older than age gate.
+  - 'minimatch'
```

### lavamoat/browserify/beta/policy.json
```diff
@@ -3655,7 +3655,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6246,7 +6246,7 @@
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
@@ -3655,7 +3655,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6246,7 +6246,7 @@
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
@@ -3655,7 +3655,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6246,7 +6246,7 @@
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
@@ -3655,7 +3655,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "packages": {
         "process": true,
         "semver": true
@@ -6246,7 +6246,7 @@
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
@@ -3602,7 +3602,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "globals": {
         "process.version": true
       },
@@ -6339,7 +6339,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```

### lavamoat/webpack/mv2/experimental/policy.json
```diff
@@ -3602,7 +3602,7 @@
         "buffer>ieee754": true
       }
     },
-    "eslint-plugin-n>builtins": {
+    "@metamask/snaps-utils>validate-npm-package-name>builtins": {
       "globals": {
         "process.version": true
       },
@@ -6339,7 +6339,7 @@
     },
     "@metamask/snaps-utils>validate-npm-package-name": {
       "packages": {
-        "eslint-plugin-n>builtins": true
+        "@metamask/snaps-utils>validate-npm-package-name>builtins": true
       }
     },
     "react-markdown>vfile>vfile-message": {
```
