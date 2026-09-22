# [H] txtdot SSRF vulnerability in /proxy

## Summary
Severity: High
Advisory: CVE-2024-41813
Aliases: GHSA-4c78-229v-hf6m
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-07-26
Source: https://osv.dev/vulnerability/CVE-2024-41813
Type: osv

## Details
txtdot is an HTTP proxy that parses only text, links, and pictures from pages, removing ads and heavy scripts. Starting in version 1.4.0 and prior to version 1.6.1, a Server-Side Request Forgery (SSRF) vulnerability in the `/proxy` route of txtdot allows remote attackers to use the server as a proxy to send HTTP GET requests to arbitrary targets and retrieve information in the internal network. Version 1.6.1 patches the issue.

## References
- https://github.com/TxtDot/txtdot/blob/a7fdaf80fdf45abefe83b2eb5135ba112142dc74/src/handlers/distributor.ts#L43-L47
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41813.json
- https://github.com/TxtDot/txtdot/security/advisories/GHSA-4c78-229v-hf6m
- https://nvd.nist.gov/vuln/detail/CVE-2024-41813
- https://github.com/TxtDot/txtdot/commit/f241a46e05b148a39b84bf956051b5aaa489949e
