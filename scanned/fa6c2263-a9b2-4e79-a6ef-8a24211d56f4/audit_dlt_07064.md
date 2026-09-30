# [?] [SharovBot] docs/site: pin qs to ^6.16.0 to resolve security advisory (#23763)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-09-03
Source: https://github.com/erigontech/erigon/commit/42747db9920a0627c656e492b07e332489df6fb1
Type: security-commit

## Details
[SharovBot] docs/site: pin qs to ^6.16.0 to resolve security advisory (#23763)

**[SharovBot]**

## Summary

Dependabot has been flagging a security advisory on the `qs` npm package
in `docs/site`. The package has known vulnerabilities in versions <
6.16.0. Dependabot cannot auto-update it because it is a transitive
dependency of `@docusaurus/*` packages which constrain the version via
their own dependency ranges.

## Fix

Add an `overrides` entry in `docs/site/package.json` to force `qs` to
`^6.16.0` across all transitive dependents:

```json
"overrides": {
  "qs": "^6.16.0"
}
```

This is the standard npm approach when a vulnerable transitive
dependency cannot be updated by updating the direct dependency.

## Affected Security Advisories

- `qs` < 6.16.0 — multiple CVEs affecting prototype pollution and query
string parsing

---------

Co-authored-by: SharovBot <bot@erigon.tech>
Co-authored-by: Giulio Rebuffo <giulio.rebuffo@gmail.com>
Co-authored-by: Alex Sharov <AskAlexSharov@gmail.com>

## Patch
### docs/site/package-lock.json
```diff
@@ -16824,12 +16824,13 @@
       }
     },
     "node_modules/qs": {
-      "version": "6.15.2",
-      "resolved": "https://registry.npmjs.org/qs/-/qs-6.15.2.tgz",
-      "integrity": "sha512-Rzq0KEyX/w/tEybncDgdkZrJgVUsUMk3xjh3t5bv3S1HTAtg+uOYt72+ZfwiQwKdysThkTBdL/rTi6HDmX9Ddw==",
+      "version": "6.16.0",
+      "resolved": "https://registry.npmjs.org/qs/-/qs-6.16.0.tgz",
+      "integrity": "sha512-h6fhOIaRrID2CbEY2fqs+7t+UXZo+MLAnU5gRIq85uFtdiUPCdsApMlHhXogKVM4HM2DVbIjGNTTYH2OcmP1vA==",
       "license": "BSD-3-Clause",
       "dependencies": {
-        "side-channel": "^1.1.0"
+        "es-define-property": "^1.0.1",
+        "side-channel": "^1.1.1"
       },
       "engines": {
         "node": ">=0.6"
@@ -18090,14 +18091,14 @@
       }
     },
     "node_modules/side-channel": {
-      "version": "1.1.0",
-      "resolved": "https://registry.npmjs.org/side-channel/-/side-channel-1.1.0.tgz",
-      "integrity": "sha512-ZX99e6tRweoUXqR+VBrslhda51Nh5MTQwou5tnUDgbtyM0dBgmhEDtWGP/xbKn6hqfPRHujUNwz5fy/wbbhnpw==",
+      "version": "1.1.1",
+      "resolved": "https://registry.npmjs.org/side-channel/-/side-channel-1.1.1.tgz",
+      "integrity": "sha512-6x6dK6zJdpTzF4sQeNYxwtvBzf6Eg4GtlesS94HOvTudUeyK2WXAaIfmDgsyslYrRBeFIlsi54AYsFGUuhmvrQ==",
       "license": "MIT",
       "dependencies": {
         "es-errors": "^1.3.0",
-        "object-inspect": "^1.13.3",
-        "side-channel-list": "^1.0.0",
+        "object-inspect": "^1.13.4",
+        "side-channel-list": "^1.0.1",
         "side-channel-map": "^1.0.1",
         "side-channel-weakmap": "^1.0.2"
       },
```

### docs/site/package.json
```diff
@@ -68,6 +68,7 @@
     },
     "webpack-dev-server": {
       "ws": "^8.20.1"
-    }
+    },
+    "qs": "^6.16.0"
   }
 }
```
