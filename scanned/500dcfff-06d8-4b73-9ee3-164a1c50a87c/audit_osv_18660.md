# [C] CVE-2020-29663

## Summary
Severity: Critical
Advisory: CVE-2020-29663
Aliases: GHSA-pcmr-2p2f-r7j6
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-12-15
Source: https://osv.dev/vulnerability/CVE-2020-29663
Type: osv

## Details
Icinga 2 v2.8.0 through v2.11.7 and v2.12.2 has an issue where revoked certificates due for renewal will automatically be renewed, ignoring the CRL. This issue is fixed in Icinga 2 v2.11.8 and v2.12.3.

## References
- https://github.com/Icinga/icinga2/security/advisories/GHSA-pcmr-2p2f-r7j6
- https://github.com/Icinga/icinga2/compare/v2.12.1...v2.12.2
