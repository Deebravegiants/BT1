# [C] CVE-2019-15679

## Summary
Severity: Critical
Advisory: CVE-2019-15679
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-15679
Type: osv

## Details
TightVNC code version 1.3.10 contains heap buffer overflow in InitialiseRFBConnection function, which can potentially result code execution. This attack appear to be exploitable via network connectivity.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-478893.pdf
- https://lists.debian.org/debian-lts-announce/2019/12/msg00028.html
- https://www.openwall.com/lists/oss-security/2018/12/10/5
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-08
