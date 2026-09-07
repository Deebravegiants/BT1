# [M] Gin Web Framework does not properly sanitize filename parameter of Context.FileAttachment function

## Summary
Severity: Medium
Advisory: GHSA-2c4m-59x9-fr2g
CVE: CVE-2023-29401
CWE: CWE-494
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-05-12
Source: https://github.com/advisories/GHSA-2c4m-59x9-fr2g
Type: github-advisory

## Affected
- Go: `github.com/gin-gonic/gin` — affected >=1.3.1-0.20190301021747-ccb9e902956d <1.9.1

## Details
The filename parameter of the Context.FileAttachment function is not properly sanitized. A maliciously crafted filename can cause the Content-Disposition header to be sent with an unexpected filename value or otherwise modify the Content-Disposition header. For example, a filename of "setup.bat&quot;;x=.txt" will be sent as a file named "setup.bat".

If the FileAttachment function is called with names provided by an untrusted source, this may permit an attacker to cause a file to be served with a name different than provided. Maliciously crafted attachment file name can modify the Content-Disposition header.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-29401
- https://github.com/gin-gonic/gin/issues/3555
- https://github.com/gin-gonic/gin/pull/3556
- https://github.com/gin-gonic/gin
- https://github.com/gin-gonic/gin/releases/tag/v1.9.1
- https://pkg.go.dev/vuln/GO-2023-1737
