# [H] h2o is vulnerable to musl libc stack overflow

## Summary
Severity: High
Advisory: CVE-2026-44453
Aliases: GHSA-rf9v-m59p-mq84
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-44453
Type: osv

## Details
h2o is an HTTP server with support for HTTP/1.x, HTTP/2 and HTTP/3. Prior to commit 6b5370d, h2o is vulnerable to a Denial of Service attack when calling alloca under certain conditions. When serving static files, h2o builds the file path on stack, by calling alloca. The maximum size of the memory allocated using alloca can be as huge as ~600KB, which exceeds the default pthread stack size used by musl libc (128KB). If the amount of memory allocated by alloca exceeds the stack size, the h2o server crashes with a segmentation fault, while it tries to touch the guard page. This issue has been fixed by commit 6b5370d.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44453.json
- https://github.com/h2o/h2o/security/advisories/GHSA-rf9v-m59p-mq84
- https://nvd.nist.gov/vuln/detail/CVE-2026-44453
- https://github.com/h2o/h2o/commit/6b5370d9d09fcf83aa7620ddf77de1954a192181
