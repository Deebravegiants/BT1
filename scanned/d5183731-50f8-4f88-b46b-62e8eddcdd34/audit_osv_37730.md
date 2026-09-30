# [H] AVideo-Encoder is Vulnerable to Authenticated SQL Injection via ORDER BY Clause

## Summary
Severity: High
Advisory: CVE-2026-33025
Aliases: GHSA-5qvj-5h75-27pj
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-20
Source: https://osv.dev/vulnerability/CVE-2026-33025
Type: osv

## Details
AVideo is a video-sharing Platform. Versions prior to 8.0 contain a SQL Injection vulnerability in the getSqlFromPost() method of Object.php. The $_POST['sort'] array keys are used directly as SQL column identifiers inside an ORDER BY clause. Although real_escape_string() was applied, it only escapes string-context characters (quotes, null bytes) and provides no protection for SQL identifiers — making it entirely ineffective here. This issue has been fixed in version 8.0. To workaround this issue without upgrading, operators can apply a WAF rule to block POST requests where any sort[*] key contains characters outside [A-Za-z0-9_]. Alternatively, restrict access to the queue view (queue.json.php, index.php) to trusted IP ranges only.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33025.json
- https://github.com/WWBN/AVideo-Encoder/security/advisories/GHSA-5qvj-5h75-27pj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33025
- https://github.com/WWBN/AVideo-Encoder/commit/d1c8a17ac88b5e27da9dfb7a230bbaf54aa53124
