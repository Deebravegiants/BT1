# [?] docs: note on security advisory in release notes for versions `0.2.15`, `0.2.16`, and `0.3.0` (#3553)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-08-06
Source: https://github.com/vyperlang/vyper/commit/cc2a5cd696f9720683a19a9490119ee7297a4192
Type: security-commit

## Details
docs: note on security advisory in release notes for versions `0.2.15`, `0.2.16`, and `0.3.0` (#3553)

* Add note on security advisory in release notes for `0.2.15`, `0.2.16`, and `0.3.0`

* Add link to `0.3.1` release

## Patch
### docs/release-notes.rst
```diff
@@ -336,6 +336,7 @@ Special thanks to @skellet0r for some major features in this release!
 
 v0.3.0
 *******
+⚠️ A critical security vulnerability has been discovered in this version and we strongly recommend using version `0.3.1 <https://github.com/vyperlang/vyper/releases/tag/v0.3.1>`_ or higher. For more information, please see the Security Advisory `GHSA-5824-cm3x-3c38 <https://github.com/vyperlang/vyper/security/advisories/GHSA-5824-cm3x-3c38>`_.
 
 Date released: 2021-10-04
 
@@ -368,6 +369,7 @@ Special thanks to contributions from @skellet0r and @benjyz for this release!
 
 v0.2.16
 *******
+⚠️ A critical security vulnerability has been discovered in this version and we strongly recommend using version `0.3.1 <https://github.com/vyperlang/vyper/releases/tag/v0.3.1>`_ or higher. For more information, please see the Security Advisory `GHSA-5824-cm3x-3c38 <https://github.com/vyperlang/vyper/security/advisories/GHSA-5824-cm3x-3c38>`_.
 
 Date released: 2021-08-27
 
@@ -392,6 +394,7 @@ Special thanks to contributions from @skellet0r, @sambacha and @milancermak for
 
 v0.2.15
 *******
+⚠️ A critical security vulnerability has been discovered in this version and we strongly recommend using version `0.3.1 <https://github.com/vyperlang/vyper/releases/tag/v0.3.1>`_ or higher. For more information, please see the Security Advisory `GHSA-5824-cm3x-3c38 <https://github.com/vyperlang/vyper/security/advisories/GHSA-5824-cm3x-3c38>`_.
 
 Date released: 23-07-2021
 
```
