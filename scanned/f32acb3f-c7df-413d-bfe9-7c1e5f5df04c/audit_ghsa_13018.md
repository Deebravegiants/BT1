# [C] SES's dynamic import and spread operator provides possible path to arbitrary exfiltration and execution

## Summary
Severity: Critical
Advisory: GHSA-9c4h-3f7h-322r
CVE: CVE-2023-39532
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-09
Source: https://github.com/advisories/GHSA-9c4h-3f7h-322r
Type: github-advisory

## Affected
- npm: `ses` — affected >=0.13.0 <0.13.5
- npm: `ses` — affected >=0.14.0 <0.14.5
- npm: `ses` — affected >=0.15.0 <0.15.24
- npm: `ses` — affected >=0.16.0 <0.16.1
- npm: `ses` — affected >=0.17.0 <0.17.1
- npm: `ses` — affected >=0.18.0 <0.18.7

## Details
### Impact

This is a hole in the confinement of guest applications under SES that may manifest as either the ability to exfiltrate information or execute arbitrary code depending on the configuration and implementation of the surrounding host.

Guest program running inside a Compartment with as few as no endowments can gain access to the surrounding host’s dynamic import by using dynamic import after the spread operator, like `{...import(arbitraryModuleSpecifier)}`.

On the web or in web extensions, a Content-Security-Policy following ordinary best practices likely mitigates both the risk of exfiltration and execution of arbitrary code, at least limiting the modules that the attacker can import to those that are already part of the application. However, without a Content-Security-Policy, dynamic import can be used to issue HTTP requests for either communication through the URL or for the execution of code reachable from that origin.

Within an XS worker, an attacker can use the host’s module system to the extent that the host has been configured. This typically only allows access to module code on the host’s file system and is of limited use to an attacker.

Within Node.js, the attacker gains access to Node.js’s module system. Importing the powerful builtins is not useful except insofar as there are side-effects and tempered because dynamic import returns a promise. Spreading a promise into an object renders the promises useless. However, Node.js allows importing data URLs, so this is a clear path to arbitrary execution.

### Patches

All affected `0.*` version trains have the following patch. Running `npm update` will obtain the patch on all affected projects using `^0.*` style dependency constraints in their `package.json`.

```diff
From 33469e88bfb2bf34a161c265f10f808ce354a700 Mon Sep 17 00:00:00 2001
From: Kris Kowal <kris@agoric.com>
Date: Thu, 27 Jul 2023 13:25:13 -0700
Subject: [PATCH] fix(fix): Censor spread import

---
 packages/ses/src/transforms.js       |  2 +-
 packages/ses/test/test-transforms.js | 22 +++++++++++++++++++++-
 2 files changed, 22 insertions(+), 2 deletions(-)

diff --git a/packages/ses/src/transforms.js b/packages/ses/src/transforms.js
index a0fc8d0ef..64a46cb53 100644
--- a/packages/ses/src/transforms.js
+++ b/packages/ses/src/transforms.js
@@ -106,7 +106,7 @@ export const evadeHtmlCommentTest = src => {
 // /////////////////////////////////////////////////////////////////////////////
 
 const importPattern = new FERAL_REG_EXP(
-  '(^|[^.])\\bimport(\\s*(?:\\(|/[/*]))',
+  '(^|[^.]|\\.\\.\\.)\\bimport(\\s*(?:\\(|/[/*]))',
   'g',
 );
 
diff --git a/packages/ses/test/test-transforms.js b/packages/ses/test/test-transforms.js
index cef0c02c1..8f6818b83 100644
--- a/packages/ses/test/test-transforms.js
+++ b/packages/ses/test/test-transforms.js
@@ -6,7 +6,7 @@ import {
 } from '../src/transforms.js';
 
 test('no-import-expression regexp', t => {
-  t.plan(9);
+  t.plan(13);
 
   // Note: we cannot define these as regular functions (and then stringify)
   // because the 'esm' module loader that we use for running the tests (i.e.
@@ -20,6 +20,7 @@ test('no-import-expression regexp', t => {
   const safe = 'const a = 1';
   const safe2 = "const a = notimport('evil')";
   const safe3 = "const a = importnot('evil')";
+  const safe4 = "const a = compartment.import('name')";
 
   const obvious = "const a = import('evil')";
   const whitespace = "const a = import ('evil')";
@@ -27,10 +28,14 @@ test('no-import-expression regexp', t => {
   const doubleSlashComment = "const a = import // hah\n('evil')";
   const newline = "const a = import\n('evil')";
   const multiline = "\nimport('a')\nimport('b')";
+  const spread = "{...import('exfil')}";
+  const spread2 = "{\n...\nimport\n('exfil')}";
+  const spread3 = "{\n...\nimport/**/\n('exfil')}";
 
   t.is(rejectImportExpressions(safe), safe, 'safe');
   t.is(rejectImportExpressions(safe2), safe2, 'safe2');
   t.is(rejectImportExpressions(safe3), safe3, 'safe3');
+  t.is(rejectImportExpressions(safe4), safe4, 'safe4');
   t.throws(
     () => rejectImportExpressions(obvious),
     { instanceOf: SyntaxError },
@@ -62,6 +67,21 @@ test('no-import-expression regexp', t => {
     'possible import expression rejected around line 2',
     'multiline',
   );
+  t.throws(
+    () => rejectImportExpressions(spread),
+    { instanceOf: SyntaxError },
+    'spread',
+  );
+  t.throws(
+    () => rejectImportExpressions(spread2),
+    { instanceOf: SyntaxError },
+    'spread2',
+  );
+  t.throws(
+    () => rejectImportExpressions(spread3),
+    { instanceOf: SyntaxError },
+    'spread3',
+  );
 });
 
 test('no-html-comment-expression regexp', t => {
-- 
2.40.1
```

### Workarounds

On the web, providing a suitably constrained Content-Security-Policy mitigates most of the threat.

With XS, building a binary that lacks the ability to load modules at runtime mitigates the entirety of the threat. That will look like an implementation of `fxFindModule` in a file like `xsPlatform.c` that calls `fxRejectModuleFile`.

We highly advise applying the above patch for Node.js as there is no known work-around and Node.js’s module specifiers are exceedingly powerful, including support for `data:text/javascript,` style module specifier URLs.

### References

No references at this time.

## References
- https://github.com/endojs/endo/security/advisories/GHSA-9c4h-3f7h-322r
- https://nvd.nist.gov/vuln/detail/CVE-2023-39532
- https://github.com/endojs/endo/commit/fc90c6429604dc79ce8e3355e236ccce2bada041
- https://github.com/endojs/endo
