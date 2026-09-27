# [H] JLSEC-2026-400

## Summary
Severity: High
Advisory: JLSEC-2026-400
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-400
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.5.0+0
- Julia: `LibCURL_jll` — affected >=7.81.0+0 <7.87.0+0

## Details
A vulnerability exists in curl <7.87.0 HSTS check that could be bypassed to trick it to keep using HTTP. Using its HSTS support, curl can be instructed to use HTTPS instead of using an insecure clear-text HTTP step even when HTTP is provided in the URL. However, the HSTS mechanism could be bypassed if the host name in the given URL first uses IDN characters that get replaced to ASCII counterparts as part of the IDN conversion. Like using the character UTF-8 U+3002 (IDEOGRAPHIC FULL STOP) instead of the common ASCII full stop (U+002E) `.`. Then in a subsequent request, it does not detect the HSTS state and makes a clear text transfer. Because it would store the info IDN encoded but look for it IDN decoded.

## References
- https://hackerone.com/reports/1755083
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TVWZW5CNSJ7UYAF2BGSYAWAEXDJYUBHA/
- https://security.gentoo.org/glsa/202310-12
- https://security.netapp.com/advisory/ntap-20230427-0007/
