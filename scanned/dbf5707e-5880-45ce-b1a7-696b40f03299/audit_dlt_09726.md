# [?] docs(security): clarify released vulnerability disclosure scope

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-24
Source: https://github.com/fedimint/fedimint/commit/e62ab223ac1ec976e747ec7aadd0746216755428
Type: security-commit

## Details
docs(security): clarify released vulnerability disclosure scope

### Summary

The security policy now limits private disclosure requirements to vulnerabilities affecting released Fedimint code. It permits public reporting and discussion of bugs confined to unreleased changes, while preserving private handling when a finding in unreleased code also affects a released version. This removes ambiguity for public review without weakening protection for deployed releases.

### Details

Previously, the blanket public-issue prohibition and private-until-fix guidance could be read to cover every security bug, including bugs only in proposed code. Both statements now state the released-code boundary explicitly. A newly introduced bug may be discussed publicly; a bug exposed by new changes that is also present in a released version remains private until the release-fix process completes.

### Reviews

Independent review passed with no findings.

## Patch
### SECURITY.md
```diff
@@ -2,7 +2,10 @@
 
 ## Reporting a Vulnerability
 
-Do **not** open a public GitHub issue for security bugs.
+Do **not** open a public GitHub issue for security bugs that affect released
+code. Bugs confined to unreleased code may be reported and discussed publicly.
+If an unreleased change exposes a vulnerability that also affects a released
+version, report it privately.
 
 Send a report to **security@fedimint.org** (this address forwards to the
 maintainers listed below) or message **`@elsirion.21`** on Signal.
@@ -34,8 +37,9 @@ gpg --fetch-keys 'https://api.protonmail.ch/pks/lookup?op=get&search=elsirion@pr
 
 Check the fingerprints against the table above before you use the keys.
 
-Please keep the bug private until a fix is released and federation operators
-had time to upgrade.
+Please keep vulnerabilities affecting released code private until a fix is
+released and federation operators had time to upgrade. Bugs confined to
+unreleased code do not require private handling.
 
 ## Supported Versions
 
```
