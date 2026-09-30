# [H] CVE-2019-15680

## Summary
Severity: High
Advisory: CVE-2019-15680
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-15680
Type: osv

## Details
TightVNC code version 1.3.10 contains null pointer dereference in HandleZlibBPP function, which results Denial of System (DoS). This attack appear to be exploitable via network connectivity.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-478893.pdf
- https://lists.debian.org/debian-lts-announce/2019/12/msg00028.html
- https://usn.ubuntu.com/4407-1/
- https://us-cert.cisa.gov/ics/advisories/icsa-20-343-08
- https://www.openwall.com/lists/oss-security/2018/12/10/5
