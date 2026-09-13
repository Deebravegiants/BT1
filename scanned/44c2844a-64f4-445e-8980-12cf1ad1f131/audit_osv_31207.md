# [M] SSRF and Partial LFI in /models/apply Endpoint in mudler/localai

## Summary
Severity: Medium
Advisory: CVE-2024-6095
CVSS: 5.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N)
Published: 2024-07-06
Source: https://osv.dev/vulnerability/CVE-2024-6095
Type: osv

## Details
A vulnerability in the /models/apply endpoint of mudler/localai versions 2.15.0 allows for Server-Side Request Forgery (SSRF) and partial Local File Inclusion (LFI). The endpoint supports both http(s):// and file:// schemes, where the latter can lead to LFI. However, the output is limited due to the length of the error message. This vulnerability can be exploited by an attacker with network access to the LocalAI instance, potentially allowing unauthorized access to internal HTTP(s) servers and partial reading of local files. The issue is fixed in version 2.17.

## References
- https://huntr.com/bounties/4799262d-72dc-43c8-bc99-81d0dce996dc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6095.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6095
- https://github.com/mudler/localai/commit/2fc6fe806b903ac0a70218b21b5c84443a1b0866
