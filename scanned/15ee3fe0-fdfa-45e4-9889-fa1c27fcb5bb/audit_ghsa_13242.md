# [M] Salt vulnerable to denial of service

## Summary
Severity: Medium
Advisory: GHSA-vpjg-wmf8-29h9
CVE: CVE-2023-20897
CWE: CWE-404
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2023-09-05
Source: https://github.com/advisories/GHSA-vpjg-wmf8-29h9
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3005.2
- PyPI: `salt` — affected >=3006.0rc1 <3006.2

## Details
Salt masters prior to 3005.2 or 3006.2 contain a DOS in minion return. After receiving several bad packets on the request server equal to the number of worker threads, the master will become unresponsive to return requests until restarted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20897
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2023-166.yaml
- https://github.com/saltstack/salt
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OMWJIHQZXHK6FH2E3IWAZCYIRI7FLVOL
- https://saltproject.io/security-announcements/2023-08-10-advisory
