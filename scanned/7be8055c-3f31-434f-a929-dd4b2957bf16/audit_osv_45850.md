# [M] JLSEC-2026-403

## Summary
Severity: Medium
Advisory: JLSEC-2026-403
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-403
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=7.81.0+0 <7.88.1+0

## Details
A cleartext transmission of sensitive information vulnerability exists in curl <v7.88.0 that could cause HSTS functionality to behave incorrectly when multiple URLs are requested in parallel. Using its HSTS support, curl can be instructed to use HTTPS instead of using an insecure clear-text HTTP step even when HTTP is provided in the URL. This HSTS mechanism would however surprisingly fail when multiple transfers are done in parallel as the HSTS cache file gets overwritten by the most recentlycompleted transfer. A later HTTP-only transfer to the earlier host name would then *not* get upgraded properly to HSTS.

## References
- https://hackerone.com/reports/1826048
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230309-0006/
