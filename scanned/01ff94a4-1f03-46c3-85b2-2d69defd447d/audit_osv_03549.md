# [H] ALPINE-CVE-2026-28387

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-28387
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-28387
Type: osv

## Affected
- Alpine:v3.20: `openssl` — affected >=1.1.1 <3.3.7-r0
- Alpine:v3.21: `openssl` — affected >=1.1.1 <3.3.7-r0
- Alpine:v3.22: `openssl` — affected >=1.1.1 <3.5.6-r0
- Alpine:v3.23: `openssl` — affected >=1.1.1 <3.5.6-r0
- Alpine:v3.24: `openssl` — affected >=1.1.1 <3.5.6-r0

## Details
Issue summary: An uncommon configuration of clients performing DANE TLSA-based
server authentication, when paired with uncommon server DANE TLSA records, may
result in a use-after-free and/or double-free on the client side.

Impact summary: A use after free can have a range of potential consequences
such as the corruption of valid data, crashes or execution of arbitrary code.

However, the issue only affects clients that make use of TLSA records with both
the PKIX-TA(0/PKIX-EE(1) certificate usages and the DANE-TA(2) certificate
usage.

By far the most common deployment of DANE is in SMTP MTAs for which RFC7672
recommends that clients treat as 'unusable' any TLSA records that have the PKIX
certificate usages.  These SMTP (or other similar) clients are not vulnerable
to this issue.  Conversely, any clients that support only the PKIX usages, and
ignore the DANE-TA(2) usage are also not vulnerable.

The client would also need to be communicating with a server that publishes a
TLSA RRset with both types of TLSA records.

No FIPS modules are affected by this issue, the problem code is outside the
FIPS module boundary.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-28387
