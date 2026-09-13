# [H] CVE-2021-40568

## Summary
Severity: High
Advisory: CVE-2021-40568
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-01-13
Source: https://osv.dev/vulnerability/CVE-2021-40568
Type: osv

## Details
A buffer overflow vulnerability exists in Gpac through 1.0.1 via a malformed MP4 file in the svc_parse_slice function in av_parsers.c, which allows attackers to cause a denial of service, even code execution and escalation of privileges.

## References
- https://www.debian.org/security/2023/dsa-5411
- https://github.com/gpac/gpac/issues/1900
- https://github.com/gpac/gpac/commit/f1ae01d745200a258cdf62622f71754c37cb6c30
