# [C] CVE-2018-18439

## Summary
Severity: Critical
Advisory: CVE-2018-18439
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-11-20
Source: https://osv.dev/vulnerability/CVE-2018-18439
Type: osv

## Details
DENX U-Boot through 2018.09-rc1 has a remotely exploitable buffer overflow via a malicious TFTP server because TFTP traffic is mishandled. Also, local exploitation can occur via a crafted kernel image.

## References
- http://www.openwall.com/lists/oss-security/2018/11/02/2
