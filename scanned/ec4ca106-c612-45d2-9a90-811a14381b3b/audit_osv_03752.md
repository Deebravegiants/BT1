# [M] ALPINE-CVE-2026-45191

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-45191
Ecosystem: Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2026-05-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-45191
Type: osv

## Affected
- Alpine:v3.24: `perl-net-cidr-lite` — affected >=0 <0.24-r0

## Details
Net::CIDR::Lite versions before 0.24 for Perl does not properly consider extraneous zero characters in CIDR mask values, which may allow IP ACL bypass.

Mask forms like "/00" and "/01" pass validation and parse to the same prefix as their unpadded value.

See also CVE-2026-45190.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-45191
