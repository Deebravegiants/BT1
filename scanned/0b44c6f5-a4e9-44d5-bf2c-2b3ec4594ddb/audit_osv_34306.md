# [M] The Scratch Channel's Publish Articles POST Request Can Upload Articles Without Validation

## Summary
Severity: Medium
Advisory: CVE-2025-57805
Aliases: GHSA-h5rj-2466-qr23
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-08-25
Source: https://osv.dev/vulnerability/CVE-2025-57805
Type: osv

## Details
The Scratch Channel is a news website. In versions 1 and 1.1, a POST request to the endpoint used to publish articles, can be used to post an article in any category with any date, regardless of who's logged in. This issue has been patched in version 1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57805.json
- https://github.com/The-Scratch-Channel/tsc-web-client/security/advisories/GHSA-h5rj-2466-qr23
- https://nvd.nist.gov/vuln/detail/CVE-2025-57805
