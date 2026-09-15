# [H] CVE-2018-1000052

## Summary
Severity: High
Advisory: CVE-2018-1000052
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-09
Source: https://osv.dev/vulnerability/CVE-2018-1000052
Type: osv

## Details
fmtlib version prior to version 4.1.0 (before commit 0555cea5fc0bf890afe0071a558e44625a34ba85) contains a Memory corruption (SIGSEGV), CWE-134 vulnerability in fmt::print() library function that can result in Denial of Service. This attack appear to be exploitable via Specifying an invalid format specifier in the fmt::print() function results in a SIGSEGV (memory corruption, invalid write). This vulnerability appears to have been fixed in after commit 8cf30aa2be256eba07bb1cefb998c52326e846e7.

## References
- https://github.com/fmtlib/fmt/issues/642
- https://github.com/fmtlib/fmt/commit/8cf30aa2be256eba07bb1cefb998c52326e846e7
