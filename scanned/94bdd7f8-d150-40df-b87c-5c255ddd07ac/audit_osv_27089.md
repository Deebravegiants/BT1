# [H] Code Injection in langgenius/dify

## Summary
Severity: High
Advisory: CVE-2024-10252
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10252
Type: osv

## Details
A vulnerability in langgenius/dify versions <=v0.9.1 allows for code injection via internal SSRF requests in the Dify sandbox service. This vulnerability enables an attacker to execute arbitrary Python code with root privileges within the sandbox environment, potentially leading to the deletion of the entire sandbox service and causing irreversible damage.

## References
- https://huntr.com/bounties/62c6c958-96cb-426c-aebc-c41f06b9d7b0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10252.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10252
- https://github.com/langgenius/dify/commit/4ac99ffe0e1c9f4d7c523908e91bbc7739e0a8d4
