# [M] Open redirect in wwbn/avideo

## Summary
Severity: Medium
Advisory: GHSA-34hv-f45p-4qfq
CVE: CVE-2022-27463
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-04-06
Source: https://github.com/advisories/GHSA-34hv-f45p-4qfq
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
Open redirect vulnerability in objects/login.json.php in WWBN AVideo through 11.6, allows attackers to arbitrarily redirect users from a crafted url to the login page. A patch is available on the `master` branch of the repository.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-27463
- https://github.com/WWBN/AVideo/commit/77e9aa6411ff4b97571eb82e587139ec05ff894c
- https://avideo.tube
- https://github.com/WWBN/AVideo
