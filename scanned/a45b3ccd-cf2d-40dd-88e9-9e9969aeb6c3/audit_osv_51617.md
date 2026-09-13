# [H] CVE-2021-3580

## Summary
Severity: High
Advisory: CVE-2021-3580
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-08-05
Source: https://osv.dev/vulnerability/CVE-2021-3580
Type: osv

## Details
A flaw was found in the way nettle's RSA decryption functions handled specially crafted ciphertext. An attacker could use this flaw to provide a manipulated ciphertext leading to application crash and denial of service.

## References
- https://lists.debian.org/debian-lts-announce/2021/09/msg00008.html
- https://security.gentoo.org/glsa/202401-24
- https://security.netapp.com/advisory/ntap-20211104-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=1967983
