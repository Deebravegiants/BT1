# [?] docs(security): clarify released vulnerability disclosure scope (#9197)

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-09-24
Source: https://github.com/fedimint/fedimint/commit/1e266dd33e052597b036be0a91550955ae4fb71d
Type: security-commit

## Details
docs(security): clarify released vulnerability disclosure scope (#9197)

*Posted by Tau*

### Summary

This clarifies that Fedimint's private vulnerability-reporting
requirements apply to vulnerabilities affecting released code. Bugs
confined to proposed, unreleased changes may be reported and discussed
publicly, while findings that also affect a released version remain
private until fixed and operators have had time to upgrade.

### Details

Automated reviewers have withheld security-sensitive feedback when
reviewing proposed code because the previous blanket policy appeared to
prohibit public discussion of every security bug. The policy now states
the release boundary in both the public-issue guidance and the
private-until-fix guidance. This permits public review feedback for
unreleased-only bugs without disclosing vulnerabilities in deployed
release lines.

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
