# [H] Denial of Service in BerriAI/litellm

## Summary
Severity: High
Advisory: CVE-2024-10188
Aliases: GHSA-gw2q-qw9j-rgv7, PYSEC-2026-1549
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10188
Type: osv

## Details
A vulnerability in BerriAI/litellm, as of commit 26c03c9, allows unauthenticated users to cause a Denial of Service (DoS) by exploiting the use of ast.literal_eval to parse user input. This function is not safe and is prone to DoS attacks, which can crash the litellm Python server.

## References
- https://huntr.com/bounties/96a32812-213c-4819-ba4e-36143d35e95b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10188.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10188
- https://github.com/berriai/litellm/commit/21156ff5d0d84a7dd93f951ca033275c77e4f73c
