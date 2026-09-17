# [M] Integer underflow leading to stack overflow in FPC codec decompression

## Summary
Severity: Medium
Advisory: CVE-2023-48298
Aliases: GHSA-qw9f-qv29-8938
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-12-21
Source: https://osv.dev/vulnerability/CVE-2023-48298
Type: osv

## Details
ClickHouse® is an open-source column-oriented database management system that allows generating analytical data reports in real-time. This vulnerability is an integer underflow resulting in crash due to stack buffer overflow in decompression of FPC codec. It can be triggered and exploited by an unauthenticated attacker. The vulnerability is very similar to CVE-2023-47118 with how the vulnerable function can be exploited.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48298.json
- https://github.com/ClickHouse/ClickHouse/security/advisories/GHSA-qw9f-qv29-8938
- https://nvd.nist.gov/vuln/detail/CVE-2023-48298
- https://github.com/ClickHouse/ClickHouse/pull/56795
