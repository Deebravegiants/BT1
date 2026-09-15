# [M] libcurl's URL API function [`curl_url_get()`](https://curl.se/libcurl/c/curl_url_get.html) offers...

## Summary
Severity: Medium
Advisory: JLSEC-2025-37
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-10-10
Source: https://osv.dev/vulnerability/JLSEC-2025-37
Type: osv

## Affected
- Julia: `LibCURL_jll` — affected >=8.8.0+0 <8.9.0+0

## Details
libcurl's URL API function
[`curl_url_get()`](https://curl.se/libcurl/c/curl_url_get.html) offers punycode
conversions, to and from IDN. Asking to convert a name that is exactly 256
bytes, libcurl ends up reading outside of a stack based buffer when built to
use the *macidn* IDN backend. The conversion function then fills up the
provided buffer exactly - but does not null terminate the string.

This flaw can lead to stack contents accidently getting returned as part of
the converted string.

## References
- http://www.openwall.com/lists/oss-security/2024/07/24/2
- https://curl.se/docs/CVE-2024-6874.html
- https://curl.se/docs/CVE-2024-6874.json
- https://hackerone.com/reports/2604391
- https://security.netapp.com/advisory/ntap-20240822-0004/
