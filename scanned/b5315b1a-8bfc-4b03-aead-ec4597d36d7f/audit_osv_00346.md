# [C] ALPINE-CVE-2016-9953

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-9953
Ecosystem: Alpine:v3.2, Alpine:v3.3
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-9953
Type: osv

## Affected
- Alpine:v3.2: `curl` — affected >=7.30.0 <7.52.1-r0
- Alpine:v3.3: `curl` — affected >=7.30.0 <7.52.1-r0

## Details
The verify_certificate function in lib/vtls/schannel.c in libcurl 7.30.0 through 7.51.0, when built for Windows CE using the schannel TLS backend, allows remote attackers to obtain sensitive information, cause a denial of service (crash), or possibly have unspecified other impact via a wildcard certificate name, which triggers an out-of-bounds read.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-9953
