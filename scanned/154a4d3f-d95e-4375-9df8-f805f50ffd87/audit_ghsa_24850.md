# [M] GNU Mailman Postorius Access Control Issues

## Summary
Severity: Medium
Advisory: GHSA-v83x-78q3-gr2j
CVE: CVE-2021-40347
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-v83x-78q3-gr2j
Type: github-advisory

## Affected
- PyPI: `postorius` — affected >=0 <1.3.5

## Details
An issue was discovered in `views/list.py` in GNU Mailman Postorius before 1.3.5. An attacker (logged into any account) can send a crafted POST request to unsubscribe any user from a mailing list, also revealing whether that address was subscribed in the first place.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-40347
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=993746
- https://github.com/pypa/advisory-database/tree/main/vulns/postorius/PYSEC-2021-319.yaml
- https://gitlab.com/mailman/postorius
- https://gitlab.com/mailman/postorius/-/commit/3d880c56b58bc26b32eac0799407d74b64b7474b
- https://gitlab.com/mailman/postorius/-/issues/531
- https://gitlab.com/mailman/postorius/-/tags
- https://phabricator.wikimedia.org/T289798
- https://www.debian.org/security/2021/dsa-4970
