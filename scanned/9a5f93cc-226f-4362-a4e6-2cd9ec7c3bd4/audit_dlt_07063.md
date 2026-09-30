# [?] docs: replace image-size with image-size-next to fix CVE-2025-71329/71330 (#23869)

## Summary
Severity: Unknown
Chain: Ethereum
Component: erigontech/erigon
Published: 2026-09-09
Source: https://github.com/erigontech/erigon/commit/9b658390aed2d9c5180c9f070f962fdee787b391
Type: security-commit

## Details
docs: replace image-size with image-size-next to fix CVE-2025-71329/71330 (#23869)

## Summary

Fixes dependabot alerts
[#142](https://github.com/erigontech/erigon/security/dependabot/142) and
[#143](https://github.com/erigontech/erigon/security/dependabot/143)
(`docs/site/package-lock.json`).

`image-size@2.0.2` (pulled in transitively by `@docusaurus/mdx-loader`,
used to inject `width`/`height` on local markdown images at docs-build
time) has two high-severity DoS advisories with **no upstream fix**:

-
[GHSA-5p2g-fcmc-qvqq](https://github.com/advisories/GHSA-5p2g-fcmc-qvqq)
/ CVE-2025-71329 — infinite loop parsing malformed JXL/HEIF
-
[GHSA-w3rx-r6r6-pgpr](https://github.com/advisories/GHSA-w3rx-r6r6-pgpr)
/ CVE-2025-71330 — infinite loop parsing malformed ICNS

Verified upstream `image-size/image-size` has had no code commits since
the 2.0.2 release; `first_patched_version` on both advisories is `null`;
npm's `latest` tag is still `2.0.2`.

## Fix

Adds `"image-size": "npm:image-size-next@^2.1.1"` to the existing
`overrides` block in `docs/site/package.json` (same pattern already used
there for other transitive security pins). `image-size-next` is an
actively maintained fork carrying real fixes for both loops (verified by
diffing its source against `image-size@2.0.2`: both
`ispeBox`/`entryLength` advancement loops gained a minimum-size check
plus a monotonic-progress guard).

Export surface is identical (`image-size/fromFile`: `imageSizeFromFile`,
`setConcurrency`), so it's a drop-in replacement for
`@docusaurus/mdx-loader`'s usage.

## Test plan

- [x] `npm install` in `docs/site` — resolves
`node_modules/@docusaurus/mdx-loader/node_modules/image-size` to
`image-size-next@2.1.1`
- [x] `npm audit` in `docs/site` — 19 high severity findings (incl. both
target CVEs) before, 0 after
- [x] `npm run build` in `docs/site` — succeeds
- [x] Local A/B test: built the full docs site twice (baseline
`image-size@2.0.2` vs. candidate with the override), with an added test
page referencing both an SVG and a PNG local image via markdown `![]()`
syntax. Rendered `<img>` output (including injected `width`/`height` and
content-hashed asset filenames) is byte-identical between the two
builds.
- Note: none of the 197 existing `.md`/`.mdx` files in `docs/site`
currently use markdown-syntax local images (all use raw `<img
src="/img/...">` JSX or config strings), so this dependency's parsing
code isn't exercised by current content — this PR guards against future
usage and clears the dependabot alerts.

## Patch
### docs/site/package-lock.json
```diff
@@ -3649,6 +3649,19 @@
         "react-dom": "^18.0.0 || ^19.0.0"
       }
     },
+    "node_modules/@docusaurus/mdx-loader/node_modules/image-size": {
+      "name": "image-size-next",
+      "version": "2.1.1",
+      "resolved": "https://registry.npmjs.org/image-size-next/-/image-size-next-2.1.1.tgz",
+      "integrity": "sha512-n+DFjUct+G9mxZck+lvzqrTsqBJvSHMs6iEo//W5iAgRV7oUbrh1JWmKgAEpmyRB5lw6plIQizS1wK1dvrsvAw==",
+      "license": "MIT",
+      "bin": {
+        "image-size-next": "bin/image-size-next.js"
+      },
+      "engines": {
+        "node": ">=18"
+      }
+    },
     "node_modules/@docusaurus/module-type-aliases": {
       "version": "3.10.2",
       "resolved": "https://registry.npmjs.org/@docusaurus/module-type-aliases/-/module-type-aliases-3.10.2.tgz",
@@ -11142,18 +11155,6 @@
         "node": ">= 4"
       }
     },
-    "node_modules/image-size": {
-      "version": "2.0.2",
-      "resolved": "https://registry.npmjs.org/image-size/-/image-size-2.0.2.tgz",
-      "integrity": "sha512-IRqXKlaXwgSMAMtpNzZa1ZAe8m+Sa1770Dhk8VkSsP9LS+iHD62Zd8FQKs8fbPiagBE7BzoFX23cxFnwshpV6w==",
-      "license": "MIT",
-      "bin": {
-        "image-size": "bin/image-size.js"
-      },
-      "engines": {
-        "node": ">=16.x"
-      }
-    },
     "node_modules/immediate": {
       "version": "3.3.0",
       "resolved": "https://registry.npmjs.org/immediate/-/immediate-3.3.0.tgz",
```

### docs/site/package.json
```diff
@@ -51,6 +51,7 @@
     "node": ">=20.0"
   },
   "overrides": {
+    "image-size": "npm:image-size-next@^2.1.1",
     "webpack": "5.105.0",
     "@babel/plugin-transform-modules-systemjs": "^7.29.4",
     "@babel/core": "^7.29.6",
```
