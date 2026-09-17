# [M] Hybridsessions does not expire session id on logout

## Summary
Severity: Medium
Advisory: GHSA-c7q8-m4xw-c674
CVE: CVE-2022-24444
CWE: CWE-384
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-c7q8-m4xw-c674
Type: github-advisory

## Affected
- Packagist: `silverstripe/hybridsessions` — affected >=1.0.0 <2.4.1
- Packagist: `silverstripe/hybridsessions` — affected >=2.5.0 <2.5.1

## Details
When using the hybridsessions module is used without the session-manager module installed and sessions IDs are saved to disk, unexpired SessionIDs of logged out users can still be used to make authenticated requests.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24444
- https://docs.silverstripe.org/en/4/changelogs/4.10.1
- https://forum.silverstripe.org/c/releases
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/hybridsessions/CVE-2022-24444.yaml
- https://www.silverstripe.org/blog/tag/release
- https://www.silverstripe.org/download/security-releases
- https://www.silverstripe.org/download/security-releases/cve-2022-24444
