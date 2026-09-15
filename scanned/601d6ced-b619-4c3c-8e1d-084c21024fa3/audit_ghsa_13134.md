# [M] Salt can cause Git Providers to get wrong data

## Summary
Severity: Medium
Advisory: GHSA-qvh6-3j7x-3hq7
CVE: CVE-2023-20898
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-05
Source: https://github.com/advisories/GHSA-qvh6-3j7x-3hq7
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3005.2
- PyPI: `salt` — affected >=3006.0rc1 <3006.2

## Details
Git Providers can read from the wrong environment because they get the same cache directory base name in Salt masters prior to 3005.2 or 3006.2. Anything that uses Git Providers with different environments can get garbage data or the wrong data, which can lead to wrongful data disclosure, wrongful executions, data corruption and/or crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-20898
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2023-169.yaml
- https://github.com/saltstack/salt
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/OMWJIHQZXHK6FH2E3IWAZCYIRI7FLVOL
- https://saltproject.io/security-announcements/2023-08-10-advisory
