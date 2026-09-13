# [H] Horilla vulnerable to authenticated RCE via eval() in project_bulk_archive

## Summary
Severity: High
Advisory: CVE-2025-48868
Aliases: GHSA-h6qj-pwmx-wjhw
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-24
Source: https://osv.dev/vulnerability/CVE-2025-48868
Type: osv

## Details
Horilla is a free and open source Human Resource Management System (HRMS). An authenticated Remote Code Execution (RCE) vulnerability exists in Horilla 1.3.0 due to the unsafe use of Python’s eval() function on a user-controlled query parameter in the project_bulk_archive view. This allows privileged users (e.g., administrators) to execute arbitrary system commands on the server. While having Django’s DEBUG=True makes exploitation visibly easier by returning command output in the HTTP response, this is not required. The vulnerability can still be exploited in DEBUG=False mode by using blind payloads such as a reverse shell, leading to full remote code execution. This issue has been patched in version 1.3.1.

## References
- https://drive.google.com/file/d/1XQAJilt77QxkjGEa94CsZRqZIZXa3ET9/view?usp=sharing
- https://drive.google.com/file/d/1hnI9AK3fnpVrTlTRF7aRJsKhZCDIm2Ve/view?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/48xxx/CVE-2025-48868.json
- https://github.com/horilla-opensource/horilla/security/advisories/GHSA-h6qj-pwmx-wjhw
- https://nvd.nist.gov/vuln/detail/CVE-2025-48868
- https://github.com/horilla-opensource/horilla/commit/b0aab62b3a5fe6b7114b5c58db129b3744b4d8cc
