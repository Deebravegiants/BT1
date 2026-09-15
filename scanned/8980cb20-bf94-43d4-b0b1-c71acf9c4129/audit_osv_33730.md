# [M] Linkwarden Local File Inclusion Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2025-49588
Aliases: GHSA-rfc2-x8hr-536q
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2025-07-02
Source: https://osv.dev/vulnerability/CVE-2025-49588
Type: osv

## Details
Linkwarden is a self-hosted, open-source collaborative bookmark manager to collect, organize and archive webpages. In version 2.10.2, the server accepts links of format file:///etc/passwd and doesn't do any validation before sending them to parsers and playwright, this can result in leak of other user's links (and in some cases it might be possible to leak environment secrets). This issue has been patched in version 2.10.3 which has not been made public at time of publication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/49xxx/CVE-2025-49588.json
- https://github.com/linkwarden/linkwarden/security/advisories/GHSA-rfc2-x8hr-536q
- https://nvd.nist.gov/vuln/detail/CVE-2025-49588
