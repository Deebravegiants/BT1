# [C] CVE-2025-50989

## Summary
Severity: Critical
Advisory: CVE-2025-50989
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-08-27
Source: https://osv.dev/vulnerability/CVE-2025-50989
Type: osv

## Details
OPNsense before 25.1.8 contains an authenticated command injection vulnerability in its Bridge Interface Edit endpoint (interfaces_bridge_edit.php). The span POST parameter is concatenated into a system-level command without proper sanitization or escaping, allowing an administrator to inject arbitrary shell operators and payloads. Successful exploitation results in remote code execution with the privileges of the web service (typically root), potentially leading to full system compromise or lateral movement. This vulnerability arises from inadequate input validation and improper handling of user-supplied data in backend command invocations.

## References
- https://github.com/4rdr/proofs/blob/main/info/OPNsense-25.1-Command-Injection-via-span-parameter.md
- https://github.com/opnsense/changelog/blob/640e96ed6a783254283aead0d0b744fc9143ce6d/community/25.1/25.1.8#L34
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50989.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50989
