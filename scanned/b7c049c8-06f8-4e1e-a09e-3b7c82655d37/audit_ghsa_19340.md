# [H] Navidrome Transcoding Permission Bypass Vulnerability Report

## Summary
Severity: High
Advisory: GHSA-f238-rggp-82m3
CVE: CVE-2025-48948
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-05-29
Source: https://github.com/advisories/GHSA-f238-rggp-82m3
Type: github-advisory

## Affected
- Go: `github.com/navidrome/navidrome` — affected >=0 <0.56.0

## Details
### Summary
A permission verification flaw in Navidrome allows any authenticated regular user to bypass authorization checks and perform administrator-only transcoding configuration operations, including creating, modifying, and deleting transcoding settings.

### Details
Navidrome supports transcoding functionality which, although disabled by default, should restrict configuration operations to administrators only. However, the application fails to properly validate whether a user has administrative privileges when handling transcoding configuration requests.

The vulnerability exists in the API endpoints that manage transcoding settings. When a regular user sends requests to these endpoints, the application processes them without verifying if the user has administrative privileges, despite the JWT token clearly indicating the user is not an administrator (`"adm":false`).

The affected endpoints include:
- `POST /api/transcoding` (Create transcoding configuration)
- `PUT /api/transcoding/:id` (Update transcoding configuration)
- `DELETE /api/transcoding/:id` (Delete transcoding configuration)
- `GET /api/transcoding` (List transcoding configurations)

### PoC
1. Set up Navidrome with transcoding enabled
2. Log in as a regular user (non-administrator)
3. Send the following HTTP request:

```
POST /api/transcoding HTTP/1.1
Host: 192.168.199.134:4533
Content-Length: 81
x-nd-client-unique-id: e559d130-4295-401e-b65f-be7fdd564e
accept: application/json
x-nd-authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhZG0iOmZhbHNlLCJleHAiOjE3NDY2MzIyNDEsImlhdCI6MTc0NjQ1ODk5NiwiaXNzIjoiTkQiLCJzdWIiOiJ1c2VyMSIsInVpZCI6InV3THJGcWxXNHhnNEt4QjNxMk85eTYifQ.jqv2eESY8QTAHY-oLbBmO0v8IyDXrofvXqQgXSrJ6SM
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36
content-type: application/json
Origin: http://192.168.199.134:4533
Referer: http://192.168.199.134:4533/app/
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9

{"defaultBitRate":192,"name":"trans6","command":"tran6","targetFormat":"tran6"}
```

4. The request will succeed despite the JWT token clearly indicating the user is not an administrator (`"adm":false`)
5. The same operation can be performed with administrator credentials, confirming that no authorization check is being performed

### Impact
This vulnerability allows regular users to modify critical system configurations that should be restricted to administrators only. While Navidrome does not recommend enabling transcoding in production environments, when it is enabled, proper authorization checks should still be enforced.

The security impact includes:
1. **Privilege Escalation**: Regular users can perform administrator-only actions
2. **System Configuration Tampering**: Unauthorized users can modify transcoding settings, potentially affecting system performance or functionality
3. **Potential Command Injection**: Since transcoding settings include command parameters, this could potentially lead to command injection if not properly sanitized

In the threat model where administrators are trusted but regular users are not, this vulnerability represents a significant security risk when transcoding is enabled.

## References
- https://github.com/navidrome/navidrome/security/advisories/GHSA-f238-rggp-82m3
- https://nvd.nist.gov/vuln/detail/CVE-2025-48948
- https://github.com/navidrome/navidrome/pull/4096
- https://github.com/navidrome/navidrome/commit/e5438552c63fecb6284e1b179dddae91ede869c8
- https://github.com/navidrome/navidrome
