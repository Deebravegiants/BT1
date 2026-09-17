# [H] ALPINE-CVE-2018-1000115

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000115
Ecosystem: Alpine:v3.4, Alpine:v3.5, Alpine:v3.6
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000115
Type: osv

## Affected
- Alpine:v3.4: `memcached` — affected >=0 <1.4.33-r2
- Alpine:v3.5: `memcached` — affected >=0 <1.4.33-r2
- Alpine:v3.6: `memcached` — affected >=0 <1.4.36-r2

## Details
Memcached version 1.5.5 contains an Insufficient Control of Network Message Volume (Network Amplification, CWE-406) vulnerability in the UDP support of the memcached server that can result in denial of service via network flood (traffic amplification of 1:50,000 has been reported by reliable sources). This attack appear to be exploitable via network connectivity to port 11211 UDP. This vulnerability appears to have been fixed in 1.5.6 due to the disabling of the UDP protocol by default.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000115
