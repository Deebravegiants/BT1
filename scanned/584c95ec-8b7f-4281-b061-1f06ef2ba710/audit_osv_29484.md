# [M] Improper Neutralization of Special Elements in mintplex-labs/anything-llm

## Summary
Severity: Medium
Advisory: CVE-2024-4286
CVSS: 4.9 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-05-26
Source: https://osv.dev/vulnerability/CVE-2024-4286
Type: osv

## Details
Mintplex-Labs' anything-llm application is vulnerable to improper neutralization of special elements used in an expression language statement, identified in the commit id `57984fa85c31988b2eff429adfc654c46e0c342a`. The vulnerability arises from the application's handling of user modifications by managers or admins, allowing for the modification of all existing attributes of the `user` database entity without proper checks or sanitization. This flaw can be exploited to delete user threads, denying users access to their previously submitted data, or to inject fake threads and/or chat history for social engineering attacks.

## References
- https://huntr.com/bounties/a72d2923-297c-455f-af90-715e83b3da2b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/4xxx/CVE-2024-4286.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-4286
- https://github.com/mintplex-labs/anything-llm/commit/1b35bcbeab10b77e6dbd263cceecf1b965a40789
