# [M] static-web-server vulnerable to stored Cross-site Scripting in directory listings via file names

## Summary
Severity: Medium
Advisory: GHSA-rwfq-v4hq-h7fg
CVE: CVE-2024-32966
CWE: CWE-79, CWE-80
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2024-05-01
Source: https://github.com/advisories/GHSA-rwfq-v4hq-h7fg
Type: github-advisory

## Affected
- crates.io: `static-web-server` — affected >=0 <2.30.0

## Details
### Summary
If directory listings are enabled for a directory that an untrusted user has upload privileges for, a malicious file name like `<img src=x onerror=alert(1)>.txt` will allow JavaScript code execution in the context of the web server’s domain.

### Details
SWS generally does not perform escaping of HTML entities on any values inserted in the directory listing. At the very least `file_name` and `current_path` could contain malicious data however. `file_uri` could also be malicious but the relevant scenarios seem to be all caught by hyper.

### Impact
For any web server that allow users to upload files or create directories under a name of their choosing this becomes a stored XSS vulnerability.

## References
- https://github.com/static-web-server/static-web-server/security/advisories/GHSA-rwfq-v4hq-h7fg
- https://nvd.nist.gov/vuln/detail/CVE-2024-32966
- https://github.com/static-web-server/static-web-server
- https://github.com/static-web-server/static-web-server/releases/tag/v2.30.0
