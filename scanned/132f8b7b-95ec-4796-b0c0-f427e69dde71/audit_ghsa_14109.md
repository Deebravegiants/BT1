# [M] imgproxy is vulnerable to Server-Side Request Forgery

## Summary
Severity: Medium
Advisory: GHSA-9x7h-ggc3-xg47
CVE: CVE-2023-30019
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-05-08
Source: https://github.com/advisories/GHSA-9x7h-ggc3-xg47
Type: github-advisory

## Affected
- Go: `github.com/imgproxy/imgproxy/v3` — affected >=0 <3.15.0

## Details
imgproxy prior to version 3.15.0 is vulnerable to Server-Side Request Forgery (SSRF) due to a lack of sanitization of the imageURL parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-30019
- https://github.com/imgproxy/imgproxy/commit/1a9768a2c682e88820064aa3d9a05ea234ff3cc4
- https://breakandpray.com/cve-2023-30019-ssrf-in-imgproxy
- https://github.com/imgproxy/imgproxy
- https://github.com/imgproxy/imgproxy/blob/ee9e8f0cb101ec22318caffd552a23cc0548d5ce/imagedata/download.go#L142
