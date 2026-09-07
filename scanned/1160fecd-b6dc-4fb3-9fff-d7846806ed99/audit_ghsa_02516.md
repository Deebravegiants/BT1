# [M] Improper Access Control in Dolibarr

## Summary
Severity: Medium
Advisory: GHSA-vxhc-c4qm-647p
CVE: CVE-2021-25954
CWE: CWE-284, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2021-08-11
Source: https://github.com/advisories/GHSA-vxhc-c4qm-647p
Type: github-advisory

## Affected
- Packagist: `dolibarr/dolibarr` — affected >=2.8.1 <14.0.0

## Details
In “Dolibarr” application, 2.8.1 to 13.0.4 don’t restrict or incorrectly restricts access to a resource from an unauthorized actor. A low privileged attacker can modify the Private Note which only an administrator has rights to do, the affected field is at “/adherents/note.php?id=1” endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25954
- https://github.com/Dolibarr/dolibarr/commit/8cc100012d46282799fb19f735a53b7101569377
- https://github.com/Dolibarr/dolibarr
- https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25954
