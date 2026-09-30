# [H] Denial of Service (DoS) in gaizhenbiao/chuanhuchatgpt

## Summary
Severity: High
Advisory: CVE-2024-10650
Aliases: PYSEC-2025-92
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-10650
Type: osv

## Details
An unauthenticated Denial of Service (DoS) vulnerability was identified in ChuanhuChatGPT version 20240918, which could be exploited by sending large data payloads using a multipart boundary. Although a patch was applied for CVE-2024-7807, the issue can still be exploited by sending data in groups with 10 characters in a line, with multiple lines. This can cause the system to continuously process these characters, resulting in prolonged unavailability of the service. The exploitation now requires low privilege if authentication is enabled due to a version upgrade in Gradio.

## References
- https://huntr.com/bounties/f820371d-a878-44bf-b1fd-2d837dd58eb4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/10xxx/CVE-2024-10650.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-10650
