# [H] cBioPortal Proxy Endpoint Vulnerabliity

## Summary
Severity: High
Advisory: CVE-2024-41668
Aliases: GHSA-9h44-r3c3-q7rm
CVSS: 8.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2024-07-23
Source: https://osv.dev/vulnerability/CVE-2024-41668
Type: osv

## Details
The cBioPortal for Cancer Genomics provides visualization, analysis, and download of large-scale cancer genomics data sets. When running a publicly exposed proxy endpoint without authentication, cBioPortal could allow someone to perform a Server Side Request Forgery (SSRF) attack. Logged in users could do the same on private instances. A fix has been released in version 6.0.12. As a workaround, one might be able to disable `/proxy` endpoint entirely via, for example, nginx.

## References
- https://github.com/cBioPortal/cbioportal/releases/tag/v6.0.12
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41668.json
- https://github.com/cBioPortal/cbioportal/security/advisories/GHSA-9h44-r3c3-q7rm
- https://nvd.nist.gov/vuln/detail/CVE-2024-41668
- https://www.wizlynxgroup.com/security-research-advisories/vuln/WLX-2024-004
- https://github.com/cBioPortal/cbioportal/commit/ea8642fdbda2d61d2ab34b9da7a1594680bbbcd5
- https://github.com/cBioPortal/cbioportal/pull/10884
