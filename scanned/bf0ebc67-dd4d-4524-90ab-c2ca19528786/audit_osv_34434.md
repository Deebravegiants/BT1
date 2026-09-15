# [C] LangBot has a cross-directory file upload vulnerability, which could lead to system takeover

## Summary
Severity: Critical
Advisory: CVE-2025-59835
Aliases: GHSA-7j3j-qj83-9qv4
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:P)
Published: 2025-10-02
Source: https://osv.dev/vulnerability/CVE-2025-59835
Type: osv

## Details
LangBot is a global IM bot platform designed for LLMs. In versions 4.1.0 up to but not including 4.3.5, authorized attackers can exploit the /api/v1/files/documents interface to perform arbitrary file uploads. Since this interface does not strictly restrict the storage directory of files on the server, it is possible to upload dangerous files to specific system directories. This is fixed in version 4.3.5.

## References
- https://github.com/langbot-app/LangBot/releases/tag/v4.3.5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59835.json
- https://github.com/langbot-app/LangBot/security/advisories/GHSA-7j3j-qj83-9qv4
- https://nvd.nist.gov/vuln/detail/CVE-2025-59835
- https://github.com/langbot-app/LangBot/pull/1691
