# [H] CVE-2018-6335

## Summary
Severity: High
Advisory: CVE-2018-6335
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-31
Source: https://osv.dev/vulnerability/CVE-2018-6335
Type: osv

## Details
A Malformed h2 frame can cause 'std::out_of_range' exception when parsing priority meta data. This behavior can lead to denial-of-service. This affects all supported versions of HHVM (3.25.2, 3.24.6, and 3.21.10 and below) when using the proxygen server to handle HTTP2 requests.

## References
- https://hhvm.com/blog/2018/05/04/hhvm-3.25.3.html
- https://github.com/facebook/hhvm/commit/4cb57dd753a339654ca464c139db9871fe961d56
