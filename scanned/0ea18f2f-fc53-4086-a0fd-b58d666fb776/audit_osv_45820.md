# [C] A vulnerability has been found in Cesanta Mongoose up to 7.20

## Summary
Severity: Critical
Advisory: JLSEC-2026-369
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-369
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected >=0 <7.21.0+0

## Details
A vulnerability has been found in Cesanta Mongoose up to 7.20. This affects the function `mg_tls_recv_cert` of the file mongoose.c of the component TLS 1.3 Handler. Such manipulation of the argument pubkey leads to heap-based buffer overflow. The attack may be launched remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 7.21 mitigates this issue. The name of the patch is 0d882f1b43ff2308b7486a56a9d60cd6dba8a3f1. It is advisable to upgrade the affected component. The vendor was contacted early, responded in a very professional manner and quickly released a fixed version of the affected product.

## References
- https://github.com/advisories/GHSA-7vfw-f3r2-9m2j
- https://github.com/cesanta/mongoose
- https://github.com/cesanta/mongoose/
- https://github.com/cesanta/mongoose/commit/0d882f1b43ff2308b7486a56a9d60cd6dba8a3f1
- https://github.com/cesanta/mongoose/releases/tag/7.21
- https://nvd.nist.gov/vuln/detail/CVE-2026-5244
- https://vuldb.com/submit/770063
- https://vuldb.com/vuln/354825
- https://vuldb.com/vuln/354825/cti
