# [H] ALPINE-CVE-2018-1000807

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000807
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-10-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000807
Type: osv

## Affected
- Alpine:v3.6: `py-openssl` — affected >=0 <17.5.0-r0
- Alpine:v3.7: `py-openssl` — affected >=0 <17.5.0-r0
- Alpine:v3.8: `py-openssl` — affected >=0 <17.5.0-r0

## Details
Python Cryptographic Authority pyopenssl version prior to version 17.5.0 contains a CWE-416: Use After Free vulnerability in X509 object handling that can result in Use after free can lead to possible denial of service or remote code execution.. This attack appear to be exploitable via Depends on the calling application and if it retains a reference to the memory.. This vulnerability appears to have been fixed in 17.5.0.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000807
