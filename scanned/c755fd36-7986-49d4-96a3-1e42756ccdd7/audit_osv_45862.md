# [M] libcurl did not check the server certificate of TLS connections done to a host specified as an IP...

## Summary
Severity: Medium
Advisory: JLSEC-2026-417
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-417
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=8.5.0+0 <8.9.0+0
- Julia: `LibCURL_jll` — affected >=8.5.0+0 <8.7.1+0

## Details
libcurl did not check the server certificate of TLS connections done to a host specified as an IP address, when built to use mbedTLS.  libcurl would wrongly avoid using the set hostname function when the specified hostname was given as an IP address, therefore completely skipping the certificate check. This affects all uses of TLS protocols (HTTPS, FTPS, IMAPS, POPS3, SMTPS, etc).

## References
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://www.openwall.com/lists/oss-security/2024/03/27/4
- https://curl.se/docs/CVE-2024-2466.html
- https://curl.se/docs/CVE-2024-2466.json
- https://github.com/advisories/GHSA-9xr6-qf7m-2jv5
- https://hackerone.com/reports/2416725
- https://nvd.nist.gov/vuln/detail/CVE-2024-2466
- https://security.netapp.com/advisory/ntap-20240503-0010
- https://security.netapp.com/advisory/ntap-20240503-0010/
- https://support.apple.com/kb/HT214118
- https://support.apple.com/kb/HT214119
- https://support.apple.com/kb/HT214120
- https://www.vicarius.io/vsociety/posts/tls-certificate-check-bypass-curl-with-mbedtls-cve-2024-2466-2468
