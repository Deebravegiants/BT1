# [H] Random seed leakage in Jumpserver

## Summary
Severity: High
Advisory: CVE-2023-42820
Aliases: GHSA-7prv-g565-82qp
CVSS: 7.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:L)
Published: 2023-09-26
Source: https://osv.dev/vulnerability/CVE-2023-42820
Type: osv

## Details
JumpServer is an open source bastion host. This vulnerability is due to exposing the random number seed to the API, potentially allowing the randomly generated verification codes to be replayed, which could lead to password resets. If MFA is enabled users are not affect. Users not using local authentication are also not affected. Users are advised to upgrade to either version 2.28.19 or to 3.6.5. There are no known workarounds or this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42820.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-7prv-g565-82qp
- https://nvd.nist.gov/vuln/detail/CVE-2023-42820
- https://github.com/jumpserver/jumpserver/commit/42337f0d00b2a8d45ef063eb5b7deeef81597da5
