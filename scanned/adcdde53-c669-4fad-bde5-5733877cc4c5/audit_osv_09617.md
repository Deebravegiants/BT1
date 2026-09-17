# [H] CVE-2017-1000409

## Summary
Severity: High
Advisory: CVE-2017-1000409
CVSS: 7.0 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-01
Source: https://osv.dev/vulnerability/CVE-2017-1000409
Type: osv

## Details
A buffer overflow in glibc 2.5 (released on September 29, 2006) and can be triggered through the LD_LIBRARY_PATH environment variable. Please note that many versions of glibc are not vulnerable to this issue if patched for CVE-2017-1000366.

## References
- https://security.netapp.com/advisory/ntap-20190404-0003/
- http://seclists.org/oss-sec/2017/q4/385
- https://www.exploit-db.com/exploits/43331/
