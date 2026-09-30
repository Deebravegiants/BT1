# [H] A vulnerability was determined in Cesanta Mongoose up to 7.20

## Summary
Severity: High
Advisory: JLSEC-2026-371
Ecosystem: Julia
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-30
Source: https://osv.dev/vulnerability/JLSEC-2026-371
Type: osv

## Affected
- Julia: `Mongoose_jll` — affected >=0 <7.21.0+0

## Details
A vulnerability was determined in Cesanta Mongoose up to 7.20. Affected is the function `mg_tls_verify_cert_signature` of the file mongoose.c of the component P-384 Public Key Handler. Executing a manipulation can lead to authorization bypass. The attack can be executed remotely. Attacks of this nature are highly complex. The exploitability is told to be difficult. The exploit has been publicly disclosed and may be utilized. Upgrading to version 7.21 is able to address this issue. This patch is called 0d882f1b43ff2308b7486a56a9d60cd6dba8a3f1. The affected component should be upgraded. The vendor was contacted early, responded in a very professional manner and quickly released a fixed version of the affected product.

## References
- https://github.com/advisories/GHSA-hm7q-jq63-pr78
- https://github.com/cesanta/mongoose
- https://github.com/cesanta/mongoose/
- https://github.com/cesanta/mongoose/commit/0d882f1b43ff2308b7486a56a9d60cd6dba8a3f1
- https://github.com/cesanta/mongoose/releases/tag/7.21
- https://nvd.nist.gov/vuln/detail/CVE-2026-5246
- https://vuldb.com/submit/770104
- https://vuldb.com/vuln/354827
- https://vuldb.com/vuln/354827/cti
