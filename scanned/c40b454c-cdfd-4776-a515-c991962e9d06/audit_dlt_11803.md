# [?] Replace yarn resolutions entry for `axios` security patch with version bump (#4637)

## Summary
Severity: Unknown
Chain: Tooling
Component: MetaMask/core
Published: 2024-08-23
Source: https://github.com/MetaMask/core/commit/cfb51b691be9bb5ccc9dad1242692eb48bc4ade5
Type: security-commit

## Details
Replace yarn resolutions entry for `axios` security patch with version bump (#4637)

## Explanation

- Removes yarn resolutions entry for `axios` that pinned it to a version
patched for a [level high security
threat](https://github.com/MetaMask/core/security/dependabot/58).
- Resolves security issue by updating `axios` via a `contentful` version
bump.
- `axios` is a transitive dependency of core:
`@metamask/notification-services-controller` > `contentful` > `axios`.

## References

- Fixes yarn resolutions introduced by:
https://github.com/MetaMask/core/pull/4632

## Changelog

### `@metamask/notification-services-controller`

```md
### Changed

- Bump `contentful` from `^10.3.6` to `^10.15.0` ([#4637](https://github.com/MetaMask/core/pull/4637))
```

## Checklist

- [ ] I've updated the test suite for new or updated code as appropriate
- [ ] I've updated documentation (JSDoc, Markdown, etc.) for new or
updated code as appropriate
- [ ] I've highlighted breaking changes using the "BREAKING" category
above as appropriate

## Patch
### package.json
```diff
@@ -43,7 +43,6 @@
     "pre-push": "yarn lint"
   },
   "resolutions": {
-    "axios@~1.6.8": "^1.7.4",
     "elliptic@6.5.4": "^6.5.7",
     "fast-xml-parser@^4.3.4": "^4.4.1",
     "tsup@^8.0.2": "patch:tsup@npm%3A8.0.2#./.yarn/patches/tsup-npm-8.0.2-86e40f68a7.patch",
```

### packages/notification-services-controller/package.json
```diff
@@ -46,7 +46,7 @@
     "@metamask/base-controller": "^6.0.3",
     "@metamask/controller-utils": "^11.0.2",
     "bignumber.js": "^4.1.0",
-    "contentful": "^10.3.6",
+    "contentful": "^10.15.0",
     "firebase": "^10.11.0",
     "loglevel": "^1.8.1",
     "uuid": "^8.3.2"
```

### yarn.lock
```diff
@@ -549,13 +549,13 @@ __metadata:
   languageName: node
   linkType: hard
 
-"@contentful/content-source-maps@npm:^0.6.0":
-  version: 0.6.1
-  resolution: "@contentful/content-source-maps@npm:0.6.1"
+"@contentful/content-source-maps@npm:^0.11.0":
+  version: 0.11.1
+  resolution: "@contentful/content-source-maps@npm:0.11.1"
   dependencies:
     "@vercel/stega": "npm:^0.1.2"
     json-pointer: "npm:^0.6.2"
-  checksum: 10/c29ae369959504f6e57912d1419c76c9e42549588f560f5f3b105fafd39ee709d57dc73d85afaf122acb5aa7964c301831292c654985133737592bb3d4f47482
+  checksum: 10/598e88349210aed21c9ee871250353ae15cb4130180ade9cf283261e192a80c72f8674c5533c490ad1358850e45578ed6ed4ac997b32c23b029ae4d096fa5646
   languageName: node
   linkType: hard
 
@@ -3310,7 +3310,7 @@ __metadata:
     "@types/jest": "npm:^27.4.1"
     "@types/readable-stream": "npm:^2.3.0"
     bignumber.js: "npm:^4.1.0"
-    contentful: "npm:^10.3.6"
+    contentful: "npm:^10.15.0"
     deepmerge: "npm:^4.2.2"
     firebase: "npm:^10.11.0"
     jest: "npm:^27.5.1"
@@ -6316,16 +6316,16 @@ __metadata:
   languageName: node
   linkType: hard
 
-"contentful-resolve-response@npm:^1.8.1":
-  version: 1.8.2
-  resolution: "contentful-resolve-response@npm:1.8.2"
+"contentful-resolve-response@npm:^1.9.0":
+  version: 1.9.0
+  resolution: "contentful-resolve-response@npm:1.9.0"
   dependencies:
     fast-copy: "npm:^2.1.7"
-  checksum: 10/e8936ec7c1300109f94f5301e6476d9754de71b26d4cd46f2de82e13d2096d22ca74f84ef043baadbce41f4e898b448892d56b05f8dc8715ab0f4c7964bdc309
+  checksum: 10/0c5daa59a3a6b020f9b5316812e3f14e62833b4aead008527c5bfde6549365e8e8e9f373af8836f06ca7b2023d861fdd2c241d3e74d3797133d18983be8bb3b3
   languageName: node
   linkType: hard
 
-"contentful-sdk-core@npm:^8.1.0":
+"contentful-sdk-core@npm:^8.3.1":
   version: 8.3.1
   resolution: "contentful-sdk-core@npm:8.3.1"
   dependencies:
@@ -6338,18 +6338,18 @@ __metadata:
   languageName: node
   linkType: hard
 
-"contentful@npm:^10.3.6":
-  version: 10.12.13
-  resolution: "contentful@npm:10.12.13"
+"contentful@npm:^10.15.0":
+  version: 10.15.0
+  resolution: "contentful@npm:10.15.0"
   dependencies:
-    "@contentful/content-source-maps": "npm:^0.6.0"
+    "@contentful/content-source-maps": "npm:^0.11.0"
     "@contentful/rich-text-types": "npm:^16.0.2"
-    axios: "npm:~1.6.8"
-    contentful-resolve-response: "npm:^1.8.1"
-    contentful-sdk-core: "npm:^8.1.0"
+    axios: "npm:^1.7.4"
+    contentful-resolve-response: "npm:^1.9.0"
+    contentful-sdk-core: "npm:^8.3.1"
     json-stringify-safe: "npm:^5.0.1"
     type-fest: "npm:^4.0.0"
-  checksum: 10/e4c601cbcecb2851c872bc8cc9805120af6775fe579d868621040f4ec19cf9aa380454584bb2055581b63be92564f3a00eecefd57c1f37fb91a368c10b9e2f3c
+  checksum: 10/b57c51faa99074a2f60c930c4827d1f8fe9867a359e53738532bbe859f5d72e750645fa4e195e65ad015811f344d95a0b3cebe6debef7d4e92ce9510bd55939e
   languageName: node
   linkType: hard
 
```
