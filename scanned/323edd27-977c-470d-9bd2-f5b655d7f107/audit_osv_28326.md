# [C] SSRF in mintplex-labs/anything-llm

## Summary
Severity: Critical
Advisory: CVE-2024-3149
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2024-06-06
Source: https://osv.dev/vulnerability/CVE-2024-3149
Type: osv

## Details
A Server-Side Request Forgery (SSRF) vulnerability exists in the upload link feature of mintplex-labs/anything-llm. This feature, intended for users with manager or admin roles, processes uploaded links through an internal Collector API using a headless browser. An attacker can exploit this by hosting a malicious website and using it to perform actions such as internal port scanning, accessing internal web applications not exposed externally, and interacting with the Collector API. This interaction can lead to unauthorized actions such as arbitrary file deletion and limited Local File Inclusion (LFI), including accessing NGINX access logs which may contain sensitive information.

## References
- https://huntr.com/bounties/b230d76b-ae2d-440e-a25b-94ffaa7c4ff1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/3xxx/CVE-2024-3149.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-3149
- https://github.com/mintplex-labs/anything-llm/commit/f4088d9348fa86dcebe9f97a18d39c0a6e92f15e
