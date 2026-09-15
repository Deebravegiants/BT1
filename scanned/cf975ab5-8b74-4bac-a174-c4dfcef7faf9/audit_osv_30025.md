# [M] Nginx UI's json field can construct a directory traversal payload, causing arbitrary files to be written

## Summary
Severity: Medium
Advisory: CVE-2024-49366
Aliases: GHSA-prv4-rx44-f7jr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49366
Type: osv

## Details
Nginx UI is a web user interface for the Nginx web server. Nginx UI v2.0.0-beta.35 and earlier gets the value from the json field without verification, and can construct a value value in the form of `../../`. Arbitrary files can be written to the server, which may result in loss of permissions. Version 2.0.0-beta.26 fixes the issue.

## References
- https://github.com/0xJacky/nginx-ui/releases/tag/v2.0.0-beta.36
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-prv4-rx44-f7jr
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49366.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49366
