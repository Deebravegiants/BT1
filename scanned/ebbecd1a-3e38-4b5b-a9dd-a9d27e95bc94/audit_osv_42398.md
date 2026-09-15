# [M] Potential stack-based buffer clash during tilde expansion in wordexp

## Summary
Severity: Medium
Advisory: CVE-2026-6791
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:L/SA:H/E:U)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-6791
Type: osv

## Details
When expanding paths that begin with a tilde (~) followed by a username, the internal parse_tilde function extracts the username to determine the user's home directory.  The implementation allocates memory for this username directly on the stack using the strndupa macro. Because the size of this allocation was determined by the length of the user-supplied input without any bounds checks, passing an excessively long username e.g. thousands of characters, forces the thread to exhaust its stack space. Thus if an application passes untrusted, attacker-controlled input to the wordexp function, an attacker can trigger a stack clash.

## References
- https://sourceware.org/glibc/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/6xxx/CVE-2026-6791.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-6791
- https://sourceware.org/bugzilla/show_bug.cgi?id=34091
- https://sourceware.org/git/?p=glibc.git
