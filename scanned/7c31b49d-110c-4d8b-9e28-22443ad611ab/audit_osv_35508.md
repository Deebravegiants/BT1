# [H] getnetbyaddr and getnetbyaddr_r leak stack contents to DNS resovler

## Summary
Severity: High
Advisory: CVE-2026-0915
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-01-15
Source: https://osv.dev/vulnerability/CVE-2026-0915
Type: osv

## Details
Calling getnetbyaddr or getnetbyaddr_r with a configured nsswitch.conf that specifies the library's DNS backend for networks and queries for a zero-valued network in the GNU C Library version 2.0 to version 2.42 can leak stack contents to the configured DNS resolver.

## References
- http://www.openwall.com/lists/oss-security/2026/01/16/6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/0xxx/CVE-2026-0915.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-0915
- https://sourceware.org/bugzilla/show_bug.cgi?id=33802
