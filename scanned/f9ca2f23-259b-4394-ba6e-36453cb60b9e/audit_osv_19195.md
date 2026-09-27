# [H] CVE-2020-8623

## Summary
Severity: High
Advisory: CVE-2020-8623
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-8623
Type: osv

## Details
In BIND 9.10.0 -> 9.11.21, 9.12.0 -> 9.16.5, 9.17.0 -> 9.17.3, also affects 9.10.5-S1 -> 9.11.21-S1 of the BIND 9 Supported Preview Edition, An attacker that can reach a vulnerable system with a specially crafted query packet can trigger a crash. To be vulnerable, the system must: * be running BIND that was built with "--enable-native-pkcs11" * be signing one or more zones with an RSA key * be able to receive queries from a possible attacker

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQN62GBMCIC5AY4KYADGXNKVY6AJKSJE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZKAMJZXR66P6S5LEU4SN7USSNCWTXEXP/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://kb.isc.org/docs/cve-2020-8623
- https://lists.debian.org/debian-lts-announce/2020/08/msg00053.html
- https://security.gentoo.org/glsa/202008-19
- https://security.netapp.com/advisory/ntap-20200827-0003/
- https://usn.ubuntu.com/4468-1/
- https://www.debian.org/security/2020/dsa-4752
- https://www.synology.com/security/advisory/Synology_SA_20_19
