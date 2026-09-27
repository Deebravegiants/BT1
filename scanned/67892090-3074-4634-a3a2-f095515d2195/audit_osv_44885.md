# [M] GitPython before 3.1.60 Denial of Service via ReDoS

## Summary
Severity: Medium
Advisory: CVE-2026-87819
Aliases: GHSA-g5vv-9gxw-82hx
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87819
Type: osv

## Details
GitPython before 3.1.60 contains a regular expression denial of service vulnerability in Actor.name_email_regex that processes commit author and committer fields. Attackers can craft a commit object with a malformed author field containing an unterminated angle bracket to cause quadratic backtracking, exhausting CPU resources for over two minutes per commit access.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87819.json
- https://github.com/gitpython-developers/GitPython/security/advisories/GHSA-g5vv-9gxw-82hx
- https://nvd.nist.gov/vuln/detail/CVE-2026-87819
- https://www.vulncheck.com/advisories/gitpython-before-3.1.60-denial-of-service-via-redos
