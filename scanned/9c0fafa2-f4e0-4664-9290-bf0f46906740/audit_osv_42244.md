# [M] Meshery < 1.0.57 Unauthenticated Arbitrary File Read via fileView and fileDownload

## Summary
Severity: Medium
Advisory: CVE-2026-65919
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-23
Source: https://osv.dev/vulnerability/CVE-2026-65919
Type: osv

## Details
Meshery before 1.0.57 contains an unauthenticated arbitrary file read vulnerability in the /api/system/fileView and /api/system/fileDownload endpoints that pass user-supplied file parameters directly to os.Open without path validation. Attackers can supply absolute paths or traversal sequences in the file parameter to read arbitrary files from the host filesystem without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/65xxx/CVE-2026-65919.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-65919
- https://www.vulncheck.com/advisories/meshery-unauthenticated-arbitrary-file-read-via-fileview-and-filedownload
- https://github.com/meshery/meshery/issues/20076
- https://github.com/meshery/meshery/commit/ea83a26cb090b13be36c07cf24a99f8c637cc765
- https://github.com/meshery/meshery/pull/20133
- https://github.com/meshery/meshery/releases/tag/v1.0.57
- https://github.com/meshery/meshery
