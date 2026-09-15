# [H] OpenCTI vulnerable to Denial of Service through web hook

## Summary
Severity: High
Advisory: CVE-2025-26621
Aliases: PYSEC-2025-180
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:L/A:H)
Published: 2025-05-19
Source: https://osv.dev/vulnerability/CVE-2025-26621
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. Prior to version 6.5.2, any user with the capability manage customizations can edit webhook that will execute javascript code. This can be abused to cause a denial of service attack by prototype pollution, making the node js server running the OpenCTI frontend become unavailable. Version 6.5.2 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/26xxx/CVE-2025-26621.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-gq63-jm3h-374p
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-mf88-g2wq-p7qm
- https://nvd.nist.gov/vuln/detail/CVE-2025-26621
