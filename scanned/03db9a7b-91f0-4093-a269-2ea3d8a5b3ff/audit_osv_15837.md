# [C] CVE-2019-19977

## Summary
Severity: Critical
Advisory: CVE-2019-19977
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-12-26
Source: https://osv.dev/vulnerability/CVE-2019-19977
Type: osv

## Details
libESMTP through 1.0.6 mishandles domain copying into a fixed-size buffer in ntlm_build_type_2 in ntlm/ntlmstruct.c, as demonstrated by a stack-based buffer over-read.

## References
- https://web.archive.org/web/20190528215510/http://brianstafford.info/libesmtp/
- https://github.com/Kirin-say/Vulnerabilities/blob/master/Stack_Overflow_in_libesmtp.md
- https://github.com/jbouse-debian/libesmtp/blob/ca5bd0800ef1da234315da4c59716568eb5e6402/ntlm/ntlmstruct.c#L228-L242
