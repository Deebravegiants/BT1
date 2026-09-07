# [M] Aureus ERP vulnerable to cross-site scripting in the Chatter Message Handler

## Summary
Severity: Medium
Advisory: GHSA-76c2-3q6g-xvpm
CVE: CVE-2026-4175
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-76c2-3q6g-xvpm
Type: github-advisory

## Affected
- Packagist: `aureuserp/aureuserp` — affected >=0 <1.3.0-BETA1

## Details
A vulnerability was determined in Aureus ERP up to 1.3.0-BETA1. The affected element is an unknown function of the file plugins/webkul/chatter/resources/views/filament/infolists/components/messages/content-text-entry.blade.php of the component Chatter Message Handler. Executing a manipulation of the argument subject/body can lead to cross site scripting. The attack can be launched remotely. Upgrading to version 1.3.0-BETA1 is sufficient to fix this issue. This patch is called 2135ee7efff4090e70050b63015ab5e268760ec8. It is suggested to upgrade the affected component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-4175
- https://github.com/aureuserp/aureuserp/pull/939
- https://github.com/aureuserp/aureuserp/commit/2135ee7efff4090e70050b63015ab5e268760ec8
- https://github.com/aureuserp/aureuserp
- https://github.com/aureuserp/aureuserp/releases/tag/v1.3.0-BETA1
- https://vuldb.com/?ctiid.351083
- https://vuldb.com/?id.351083
- https://vuldb.com/?submit.769827
