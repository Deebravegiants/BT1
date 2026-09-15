# [M] CVE-2020-8622

## Summary
Severity: Medium
Advisory: CVE-2020-8622
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-8622
Type: osv

## Details
In BIND 9.0.0 -> 9.11.21, 9.12.0 -> 9.16.5, 9.17.0 -> 9.17.3, also affects 9.9.3-S1 -> 9.11.21-S1 of the BIND 9 Supported Preview Edition, An attacker on the network path for a TSIG-signed request, or operating the server receiving the TSIG-signed request, could send a truncated response to that request, triggering an assertion failure, causing the server to exit. Alternately, an off-path attacker would have to correctly guess when a TSIG-signed request was sent, along with other characteristics of the packet and message, and spoof a truncated response to trigger an assertion failure, causing the server to exit.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DQN62GBMCIC5AY4KYADGXNKVY6AJKSJE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZKAMJZXR66P6S5LEU4SN7USSNCWTXEXP/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://kb.isc.org/docs/cve-2020-8622
- https://lists.debian.org/debian-lts-announce/2020/08/msg00053.html
- https://security.gentoo.org/glsa/202008-19
- https://security.netapp.com/advisory/ntap-20200827-0003/
- https://usn.ubuntu.com/4468-1/
- https://usn.ubuntu.com/4468-2/
- https://www.debian.org/security/2020/dsa-4752
- https://www.synology.com/security/advisory/Synology_SA_20_19
- https://www.oracle.com/security-alerts/cpuoct2021.html
