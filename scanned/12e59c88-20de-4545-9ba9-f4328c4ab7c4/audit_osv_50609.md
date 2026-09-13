# [H] CVE-2020-25645

## Summary
Severity: High
Advisory: CVE-2020-25645
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-10-13
Source: https://osv.dev/vulnerability/CVE-2020-25645
Type: osv

## Details
A flaw was found in the Linux kernel in versions before 5.9-rc7. Traffic between two Geneve endpoints may be unencrypted when IPsec is configured to encrypt traffic for the specific UDP port used by the GENEVE tunnel allowing anyone between the two endpoints to read the traffic unencrypted. The main threat from this vulnerability is to data confidentiality.

## References
- https://lists.debian.org/debian-lts-announce/2020/10/msg00028.html
- https://lists.debian.org/debian-lts-announce/2020/12/msg00027.html
- https://security.netapp.com/advisory/ntap-20201103-0004/
- https://www.debian.org/security/2020/dsa-4774
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00035.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00042.html
- http://packetstormsecurity.com/files/161229/Kernel-Live-Patch-Security-Notice-LSN-0074-1.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1883988
