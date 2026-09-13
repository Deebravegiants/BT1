# [M] CVE-2021-22572

## Summary
Severity: Medium
Advisory: CVE-2021-22572
Aliases: GHSA-22c6-wcjm-qfjg
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-03-29
Source: https://osv.dev/vulnerability/CVE-2021-22572
Type: osv

## Details
On unix-like systems, the system temporary directory is shared between all users on that system. The root cause is File.createTempFile creates files in the the system temporary directory with world readable permissions. Any sensitive information written to theses files is visible to all other local users on unix-like systems. We recommend upgrading past commit https://github.com/google/data-transfer-project/pull/969

## References
- https://github.com/JLLeitschuh/security-research/security/advisories/GHSA-22c6-wcjm-qfjg
- https://github.com/google/data-transfer-project/pull/969
