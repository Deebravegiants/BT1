# [C] NSClient++ Authenticated Remote Code Execution via ExternalScripts API

## Summary
Severity: Critical
Advisory: CVE-2025-34079
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2025-34079
Type: osv

## Details
An authenticated remote code execution vulnerability exists in NSClient++ version 0.5.2.35 when the web interface and ExternalScripts module are enabled. A remote attacker with the administrator password can authenticate to the web interface (default port 8443), inject arbitrary commands as external scripts via the /settings/query.json API, save the configuration, and trigger the script via the /query/{name} endpoint. The injected commands are executed with SYSTEM privileges, enabling full remote compromise.

This capability is an intended feature, but the lack of safeguards or privilege separation makes it risky when exposed to untrusted actors.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/34xxx/CVE-2025-34079.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-34079
- https://vulncheck.com/advisories/nsclient-localtoremote-system-compromise
- https://raw.githubusercontent.com/rapid7/metasploit-framework/master/modules/exploits/windows/http/nscp_authenticated_rce.rb
- https://www.exploit-db.com/exploits/48360
