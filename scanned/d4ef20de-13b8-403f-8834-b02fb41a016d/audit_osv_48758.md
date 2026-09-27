# [M] CVE-2018-12404

## Summary
Severity: Medium
Advisory: CVE-2018-12404
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-05-02
Source: https://osv.dev/vulnerability/CVE-2018-12404
Type: osv

## Details
A cached side channel attack during handshakes using RSA encryption could allow for the decryption of encrypted content. This is a variant of the Adaptive Chosen Ciphertext attack (AKA Bleichenbacher attack) and affects all NSS versions prior to NSS 3.41.

## References
- https://cert-portal.siemens.com/productcert/pdf/ssa-379803.pdf
- https://lists.debian.org/debian-lts-announce/2020/09/msg00029.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00021.html
- https://us-cert.cisa.gov/ics/advisories/icsa-21-040-04
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
- http://www.securityfocus.com/bid/107260
- https://access.redhat.com/errata/RHSA-2019:2237
- https://bugzilla.mozilla.org/show_bug.cgi?id=CVE-2018-12404
