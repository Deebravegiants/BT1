# [H] CVE-2020-8620

## Summary
Severity: High
Advisory: CVE-2020-8620
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-8620
Type: osv

## Details
In BIND 9.15.6 -> 9.16.5, 9.17.0 -> 9.17.3, An attacker who can establish a TCP connection with the server and send data on that connection can exploit this to trigger the assertion failure, causing the server to exit.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://kb.isc.org/docs/cve-2020-8620
- https://security.gentoo.org/glsa/202008-19
- https://security.netapp.com/advisory/ntap-20200827-0003/
- https://usn.ubuntu.com/4468-1/
- https://www.synology.com/security/advisory/Synology_SA_20_19
