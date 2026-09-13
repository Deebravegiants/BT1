# [H] ALPINE-CVE-2020-8265

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8265
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-01-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8265
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.13: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.23: `nodejs` — affected >=0 <14.15.4-r0
- Alpine:v3.24: `nodejs` — affected >=0 <14.15.4-r0

## Details
Node.js versions before 10.23.1, 12.20.1, 14.15.4, 15.5.1 are vulnerable to a use-after-free bug in its TLS implementation. When writing to a TLS enabled socket, node::StreamBase::Write calls node::TLSWrap::DoWrite with a freshly allocated WriteWrap object as first argument. If the DoWrite method does not return an error, this object is passed back to the caller as part of a StreamWriteResult structure. This may be exploited to corrupt memory leading to a Denial of Service or potentially other exploits.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8265
