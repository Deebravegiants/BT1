# [H] FOG SSRF via unauthenticated endpoint(s)

## Summary
Severity: High
Advisory: CVE-2023-46236
Aliases: GHSA-8qg4-9363-873h
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2023-10-31
Source: https://osv.dev/vulnerability/CVE-2023-46236
Type: osv

## Details
FOG is a free open-source cloning/imaging/rescue suite/inventory management system. Prior to version 1.5.10, a server-side-request-forgery (SSRF) vulnerability allowed an unauthenticated user to trigger a GET request as the server to an arbitrary endpoint and URL scheme. This also allows remote access to files visible to the Apache user group. Other impacts vary based on server configuration. Version 1.5.10 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/46xxx/CVE-2023-46236.json
- https://github.com/FOGProject/fogproject/security/advisories/GHSA-8qg4-9363-873h
- https://nvd.nist.gov/vuln/detail/CVE-2023-46236
- https://github.com/FOGProject/fogproject/commit/9125f35ff649a3e7fd7771b1c8e5add3c726f763
