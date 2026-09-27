# [H] Insufficient Session Expiration in alf.io

## Summary
Severity: High
Advisory: CVE-2024-25628
Aliases: GHSA-8p6m-mm22-q893
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:H)
Published: 2024-02-16
Source: https://osv.dev/vulnerability/CVE-2024-25628
Type: osv

## Details
Alf.io is a free and open source event attendance management system. In versions prior to 2.0-M4-2402 users can access the admin area even after being invalidated/deleted. This issue has been addressed in version 2.0-M4-2402. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25628.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-8p6m-mm22-q893
- https://nvd.nist.gov/vuln/detail/CVE-2024-25628
