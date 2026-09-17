# [M] CVE-2016-2053

## Summary
Severity: Medium
Advisory: CVE-2016-2053
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-02
Source: https://osv.dev/vulnerability/CVE-2016-2053
Type: osv

## Details
The asn1_ber_decoder function in lib/asn1_decoder.c in the Linux kernel before 4.3 allows attackers to cause a denial of service (panic) via an ASN.1 BER file that lacks a public key, leading to mishandling by the public_key_verify_signature function in crypto/asymmetric_keys/public_key.c.

## References
- http://www.openwall.com/lists/oss-security/2016/01/25/4
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=0d62e9dd6da45bbf0f33a8617afc5fe774c8f45f
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00044.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00054.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00021.html
- http://rhn.redhat.com/errata/RHSA-2016-2574.html
- http://www.securitytracker.com/id/1036763
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00026.html
- http://rhn.redhat.com/errata/RHSA-2016-2584.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00000.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
