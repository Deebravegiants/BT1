# [H] When an application tells libcurl it wants to allow HTTP/2 server push, and the amount of received...

## Summary
Severity: High
Advisory: JLSEC-2026-416
Ecosystem: Julia
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-05-04
Source: https://osv.dev/vulnerability/JLSEC-2026-416
Type: osv

## Affected
- Julia: `CURL_jll` — affected >=0 <8.9.0+0
- Julia: `LibCURL_jll` — affected >=0 <8.7.1+0

## Details
When an application tells libcurl it wants to allow HTTP/2 server push, and the amount of received headers for the push surpasses the maximum allowed limit (1000), libcurl aborts the server push. When aborting, libcurl inadvertently does not free all the previously allocated headers and instead leaks the memory.  Further, this error condition fails silently and is therefore not easily detected by an application.

## References
- http://seclists.org/fulldisclosure/2024/Jul/18
- http://seclists.org/fulldisclosure/2024/Jul/19
- http://seclists.org/fulldisclosure/2024/Jul/20
- http://www.openwall.com/lists/oss-security/2024/03/27/3
- https://curl.se/docs/CVE-2024-2398.html
- https://curl.se/docs/CVE-2024-2398.json
- https://github.com/advisories/GHSA-mq8w-c2j9-rqxc
- https://hackerone.com/reports/2402845
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2D44YLAUFJU6BZ4XFG2FYV7SBKXB5IZ6
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/2D44YLAUFJU6BZ4XFG2FYV7SBKXB5IZ6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GMD6UYKCCRCYETWQZUJ65ZRFULT6SHLI
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GMD6UYKCCRCYETWQZUJ65ZRFULT6SHLI/
- https://nvd.nist.gov/vuln/detail/CVE-2024-2398
- https://security.netapp.com/advisory/ntap-20240503-0009
- https://security.netapp.com/advisory/ntap-20240503-0009/
- https://support.apple.com/kb/HT214118
- https://support.apple.com/kb/HT214119
- https://support.apple.com/kb/HT214120
