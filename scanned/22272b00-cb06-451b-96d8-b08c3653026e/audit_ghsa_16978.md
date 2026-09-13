# [C] WWBN AVideo Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-mv5w-wr5c-575p
CVE: CVE-2024-31819
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-10
Source: https://github.com/advisories/GHSA-mv5w-wr5c-575p
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=12.4 <14.3

## Details
An issue in WWBN AVideo v.12.4 through v.14.2 allows a remote attacker to execute arbitrary code via the systemRootPath parameter of the submitIndex.php component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-31819
- https://github.com/WWBN/AVideo/commit/fcb1f79278684f02ee59130dc0304bd063d9d6d7
- https://chocapikk.com/posts/2024/cve-2024-31819
- https://github.com/Chocapikk/CVE-2024-31819
- https://github.com/WWBN/AVideo
