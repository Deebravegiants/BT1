# [H] CVE-2016-2226

## Summary
Severity: High
Advisory: CVE-2016-2226
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-02-24
Source: https://osv.dev/vulnerability/CVE-2016-2226
Type: osv

## Details
Integer overflow in the string_appends function in cplus-dem.c in libiberty allows remote attackers to execute arbitrary code via a crafted executable, which triggers a buffer overflow.

## References
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- http://www.openwall.com/lists/oss-security/2016/05/05/5
- https://gcc.gnu.org/bugzilla/show_bug.cgi?id=69687
- http://www.securityfocus.com/bid/90103
- https://www.exploit-db.com/exploits/42386/
