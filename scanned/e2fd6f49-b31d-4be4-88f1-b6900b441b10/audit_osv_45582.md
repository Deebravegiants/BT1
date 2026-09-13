# [M] In ssh in OpenSSH before 10.5, a use-after-free for realloc data can occur if a certain pair of...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1328
Ecosystem: Julia
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-14
Source: https://osv.dev/vulnerability/JLSEC-2026-1328
Type: osv

## Affected
- Julia: `OpenSSH_jll` — affected >=0 <10.5.1+0

## Details
In ssh in OpenSSH before 10.5, a use-after-free for realloc data can occur if a certain pair of remote-forwarding operations are concurrent.

## References
- https://github.com/advisories/GHSA-jwc3-6qvm-4r66
- https://nvd.nist.gov/vuln/detail/CVE-2026-73282
- https://www.openssh.org/releasenotes.html#10.5
