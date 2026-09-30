# [H] Improper Access Control in tooljet/tooljet

## Summary
Severity: High
Advisory: CVE-2022-3019
CVSS: 7.1 (CVSS:3.0/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-3019
Type: osv

## Details
The forgot password token basically just makes us capable of taking over the account of whoever comment in an app that we can see (bruteforcing comment id's might also be an option but I wouldn't count on it, since it would take a long time to find a valid one).

## References
- https://huntr.dev/bounties/a610300b-ce3c-4995-8337-11942b3621bf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3019.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3019
- https://github.com/tooljet/tooljet/commit/45e0d3302d92df7d7f2d609c31cea71165600b79
