# [H] Insufficient Session Expiration in pretix

## Summary
Severity: High
Advisory: GHSA-r76w-3wwq-jv6v
CVE: CVE-2023-27891
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-r76w-3wwq-jv6v
Type: github-advisory

## Affected
- PyPI: `pretix` — affected >=4.17.0 <4.17.1
- PyPI: `pretix` — affected >=4.16.0 <4.16.1
- PyPI: `pretix` — affected >=0 <4.15.1

## Details
rami.io pretix before 4.17.1 allows OAuth application authorization from a logged-out session. The fixed versions are 4.15.1, 4.16.1, and 4.17.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27891
- https://github.com/pypa/advisory-database/tree/main/vulns/pretix/PYSEC-2023-42.yaml
- https://github.com/thufschmitt/pretix-nix
- https://pretix.eu/about/en/blog/20230306-release-4171
