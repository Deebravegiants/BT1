# [H] CVE-2017-11164

## Summary
Severity: High
Advisory: CVE-2017-11164
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-07-11
Source: https://osv.dev/vulnerability/CVE-2017-11164
Type: osv

## Details
In PCRE 8.41, the OP_KETRMAX feature in the match function in pcre_exec.c allows stack exhaustion (uncontrolled recursion) when processing a crafted regular expression.

## References
- http://www.openwall.com/lists/oss-security/2023/04/12/1
- http://www.securityfocus.com/bid/99575
- https://lists.apache.org/thread.html/rf9fa47ab66495c78bb4120b0754dd9531ca2ff0430f6685ac9b07772%40%3Cdev.mina.apache.org%3E
- http://www.openwall.com/lists/oss-security/2023/04/11/1
- http://openwall.com/lists/oss-security/2017/07/11/3
