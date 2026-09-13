# [H] CVE-2017-1000408

## Summary
Severity: High
Advisory: CVE-2017-1000408
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-01
Source: https://osv.dev/vulnerability/CVE-2017-1000408
Type: osv

## Details
A memory leak in glibc 2.1.1 (released on May 24, 1999) can be reached and amplified through the LD_HWCAP_MASK environment variable. Please note that many versions of glibc are not vulnerable to this issue if patched for CVE-2017-1000366.

## References
- http://www.openwall.com/lists/oss-security/2019/06/27/7
- http://www.openwall.com/lists/oss-security/2019/06/28/1
- http://www.openwall.com/lists/oss-security/2019/06/28/2
- https://security.netapp.com/advisory/ntap-20190404-0003/
- http://seclists.org/oss-sec/2017/q4/385
- https://www.exploit-db.com/exploits/43331/
