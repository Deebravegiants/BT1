# [H] CVE-2017-11190

## Summary
Severity: High
Advisory: CVE-2017-11190
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-07-12
Source: https://osv.dev/vulnerability/CVE-2017-11190
Type: osv

## Details
unrarlib.c in unrar-free 0.0.1, when _DEBUG_LOG mode is enabled, might allow remote attackers to cause a denial of service (stack-based buffer overflow and application crash) or possibly have unspecified other impact via an RAR archive containing a long filename.

## References
- https://github.com/0x09AL/my-exploits/blob/master/pocs/unrar-free/buffer-overflow/DESCRIPTION
