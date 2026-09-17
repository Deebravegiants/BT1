# [C] DataEase has an unauthorized vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-56511
Aliases: GHSA-9f69-p73j-m73x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-10
Source: https://osv.dev/vulnerability/CVE-2024-56511
Type: osv

## Details
DataEase is an open source data visualization analysis tool. Prior to 2.10.4, there is a flaw in the authentication in the io.dataease.auth.filter.TokenFilter class, which can be bypassed and cause the risk of unauthorized access. In the io.dataease.auth.filter.TokenFilter class, ”request.getRequestURI“ is used to obtain the request URL, and it is passed to the "WhitelistUtils.match" method to determine whether the URL request is an interface that does not require authentication. The "match" method filters semicolons, but this is not enough. When users set "server.servlet.context-path" when deploying products, there is still a risk of being bypassed, which can be bypassed by any whitelist prefix /geo/../context-path/. The vulnerability has been fixed in v2.10.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56511.json
- https://github.com/dataease/dataease/security/advisories/GHSA-9f69-p73j-m73x
- https://nvd.nist.gov/vuln/detail/CVE-2024-56511
