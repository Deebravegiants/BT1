# [H] zkvyper ignored loop range bounds

## Summary
Severity: High
Advisory: CVE-2024-43366
Aliases: GHSA-8j77-7rrv-6pxx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2024-08-15
Source: https://osv.dev/vulnerability/CVE-2024-43366
Type: osv

## Details
zkvyper is a Vyper compiler. Starting in version 1.3.12 and prior to version 1.5.3, since LLL IR has no Turing-incompletness restrictions, it is compiled to a loop with a much more late exit condition. It leads to a loss of funds or other unwanted behavior if the loop body contains it. However, more real-life use cases like iterating over an array are not affected. No contracts were affected by this issue, which was fixed in version 1.5.3. Upgrading and redeploying affected contracts is the only way to avoid the vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43366.json
- https://github.com/matter-labs/era-compiler-vyper/security/advisories/GHSA-8j77-7rrv-6pxx
- https://nvd.nist.gov/vuln/detail/CVE-2024-43366
