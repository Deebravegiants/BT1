# [H] CVE-2017-5999

## Summary
Severity: High
Advisory: CVE-2017-5999
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-03-06
Source: https://osv.dev/vulnerability/CVE-2017-5999
Type: osv

## Details
An issue was discovered in sysPass 2.x before 2.1, in which an algorithm was never sufficiently reviewed by cryptographers. The fact that inc/SP/Core/Crypt.class is using the MCRYPT_RIJNDAEL_256() function (the 256-bit block version of Rijndael, not AES) instead of MCRYPT_RIJNDAEL_128 (real AES) could help an attacker to create unknown havoc in the remote system.

## References
- http://www.securityfocus.com/bid/96562
- https://cxsecurity.com/issue/WLB-2017020196
- https://github.com/nuxsmin/sysPass/commit/a0e2c485e53b370a7cc6d833e192c3c5bfd70e1f
- https://github.com/nuxsmin/sysPass/releases/tag/2.1.0.17022601
