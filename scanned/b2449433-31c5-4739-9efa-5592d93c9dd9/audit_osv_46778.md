# [H] CVE-2015-2318

## Summary
Severity: High
Advisory: CVE-2015-2318
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-08
Source: https://osv.dev/vulnerability/CVE-2015-2318
Type: osv

## Details
The TLS stack in Mono before 3.12.1 allows man-in-the-middle attackers to conduct message skipping attacks and consequently impersonate clients by leveraging missing handshake state validation, aka a "SMACK SKIP-TLS" issue.

## References
- http://www.mono-project.com/news/2015/03/07/mono-tls-vulnerability/
- http://www.openwall.com/lists/oss-security/2015/03/17/9
- http://www.securityfocus.com/bid/73253
- http://www.ubuntu.com/usn/USN-2547-1
- https://bugzilla.redhat.com/show_bug.cgi?id=1202869
- https://github.com/mono/mono/commit/1509226c41d74194c146deb173e752b8d3cdeec4
- https://mitls.org/pages/attacks/SMACK#skip
- https://www.debian.org/security/2015/dsa-3202
- http://www.openwall.com/lists/oss-security/2015/03/17/9
- https://bugzilla.redhat.com/show_bug.cgi?id=1202869
