# [H] OpenSIPS has vulnerability in the codec_delete_XX() functions

## Summary
Severity: High
Advisory: CVE-2023-27596
Aliases: GHSA-3ghx-j39m-cw4f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-15
Source: https://osv.dev/vulnerability/CVE-2023-27596
Type: osv

## Details
OpenSIPS is a Session Initiation Protocol (SIP) server implementation. Prior to versions 3.1.8 and 3.2.5, OpenSIPS crashes when a malformed SDP body is sent multiple times to an OpenSIPS configuration that makes use of the `stream_process` function. This issue was discovered during coverage guided fuzzing of the function `codec_delete_except_re`. By abusing this vulnerability, an attacker is able to crash the server. It affects configurations containing functions that rely on the affected code, such as the function `codec_delete_except_re`. This issue has been fixed in version 3.1.8 and 3.2.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27596.json
- https://github.com/OpenSIPS/opensips/security/advisories/GHSA-3ghx-j39m-cw4f
- https://nvd.nist.gov/vuln/detail/CVE-2023-27596
- https://github.com/OpenSIPS/opensips/commit/dd051f8ed5ae3347fb1d556ced3c97822c9d8450
