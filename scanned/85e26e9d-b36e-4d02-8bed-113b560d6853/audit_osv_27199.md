# [H] SSRF in parisneo/lollms-webui

## Summary
Severity: High
Advisory: CVE-2024-12766
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-12766
Type: osv

## Details
parisneo/lollms-webui version V13 (feather) suffers from a Server-Side Request Forgery (SSRF) vulnerability in the `POST /api/proxy` REST API. Attackers can exploit this vulnerability to abuse the victim server's credentials to access unauthorized web resources by specifying the JSON parameter `{"url":"http://steal.target"}`. Existing security mechanisms such as `forbid_remote_access(lollmsElfServer)`, `lollmsElfServer.config.headless_server_mode`, and `check_access(lollmsElfServer, request.client_id)` do not protect against this vulnerability.

## References
- https://huntr.com/bounties/a143a2e2-1293-4dec-b875-3312584bd2b1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/12xxx/CVE-2024-12766.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-12766
