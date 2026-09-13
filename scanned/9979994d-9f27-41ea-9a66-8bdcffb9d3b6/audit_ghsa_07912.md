# [M] funadmin has Incorrect Privilege Assignment in its Configuration Handler

## Summary
Severity: Medium
Advisory: GHSA-5m2g-4cf6-c3rg
CVE: CVE-2026-2896
CWE: CWE-266
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-02-22
Source: https://github.com/advisories/GHSA-5m2g-4cf6-c3rg
Type: github-advisory

## Affected
- Packagist: `funadmin/funadmin` — affected >=0

## Details
A weakness has been identified in funadmin up to 7.1.0-rc4. This affects the function setConfig of the file app/backend/controller/Ajax.php of the component Configuration Handler. Executing a manipulation can lead to improper authorization. The attack can be executed remotely. The exploit has been made available to the public and could be used for attacks. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-2896
- https://github.com/I4m6da/CVE/issues/3
- https://github.com/funadmin/funadmin
- https://vuldb.com/?ctiid.347207
- https://vuldb.com/?id.347207
- https://vuldb.com/?submit.753972
