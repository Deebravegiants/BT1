# [M] ALPINE-CVE-2026-47729

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-47729
Ecosystem: Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-47729
Type: osv

## Affected
- Alpine:v3.23: `squid` — affected >=0 <7.6-r0
- Alpine:v3.24: `squid` — affected >=0 <7.6-r0

## Details
Squid is a caching proxy for the Web. Prior to 7.6, due to an improper validation of syntactic correctness of input in the FTP gateway (src/clients/FtpGateway.cc), Squid is vulnerable to an out-of-bounds read: when a listing entry date in the TypeA or TypeB directory-listing formats is not followed by a filename, parsing was not restricted to the input buffer, so a trusted client accessing a misbehaving FTP server through Squid's gateway feature could read memory from random unrelated transactions. This issue is fixed in version 7.6.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-47729
