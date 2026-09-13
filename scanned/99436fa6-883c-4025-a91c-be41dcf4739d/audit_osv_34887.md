# [M] Frappe vulnerable to a path traversal allowing reading certain files

## Summary
Severity: Medium
Advisory: CVE-2025-66206
Aliases: GHSA-v4wg-gqfr-rpjm
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-12-01
Source: https://osv.dev/vulnerability/CVE-2025-66206
Type: osv

## Details
Frappe is a full-stack web application framework. Prior to 15.86.0 and 14.99.2, certain requests were vulnerable to path traversal attacks, wherein some files from the server could be retrieved if the full path was known. Sites hosted on Frappe Cloud, and even other setups that are behind a reverse proxy like NGINX are unaffected. This would mainly affect someone directly using werkzeug/gunicorn. In those cases, either an upgrade or changing the setup to use a reverse proxy is recommended. This vulnerability is fixed in 15.86.0 and 14.99.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66206.json
- https://github.com/frappe/frappe/security/advisories/GHSA-v4wg-gqfr-rpjm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66206
