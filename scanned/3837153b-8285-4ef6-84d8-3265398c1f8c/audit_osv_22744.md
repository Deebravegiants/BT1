# [C] Improper Restriction of Excessive Authentication Attempts in chatwoot/chatwoot

## Summary
Severity: Critical
Advisory: CVE-2022-3741
CVSS: 9.4 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2022-10-28
Source: https://osv.dev/vulnerability/CVE-2022-3741
Type: osv

## Details
Impact varies for each individual vulnerability in the application. For generation of accounts, it may be possible, depending on the amount of system resources available, to create a DoS event in the server. These accounts still need to be activated; however, it is possible to identify the output Status Code to separate accounts that are generated and waiting for email verification. \n\nFor the sign in directories, it is possible to brute force login attempts to either login portal, which could lead to account compromise.

## References
- https://huntr.dev/bounties/46f6e07e-f438-4540-938a-510047f987d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3741.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3741
- https://github.com/chatwoot/chatwoot/commit/9525d4f0346a2fdac13a0253f9180d20104a72d3
