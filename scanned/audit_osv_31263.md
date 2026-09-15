# [H] Timing Attack in mudler/localai

## Summary
Severity: High
Advisory: CVE-2024-7010
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-7010
Type: osv

## Details
mudler/localai version 2.17.1 is vulnerable to a Timing Attack. This type of side-channel attack allows an attacker to compromise the cryptosystem by analyzing the time taken to execute cryptographic algorithms. Specifically, in the context of password handling, an attacker can determine valid login credentials based on the server's response time, potentially leading to unauthorized access.

## References
- https://huntr.com/bounties/e286ed00-6383-47de-b5bc-9b9fad67c362
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/7xxx/CVE-2024-7010.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-7010
- https://github.com/mudler/localai/commit/db1159b6511e8fa09e594f9db0fec6ab4e142468
