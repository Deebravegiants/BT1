# [H] CVE-2020-8621

## Summary
Severity: High
Advisory: CVE-2020-8621
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-21
Source: https://osv.dev/vulnerability/CVE-2020-8621
Type: osv

## Details
In BIND 9.14.0 -> 9.16.5, 9.17.0 -> 9.17.3, If a server is configured with both QNAME minimization and 'forward first' then an attacker who can send queries to it may be able to trigger the condition that will cause the server to crash. Servers that 'forward only' are not affected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00041.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00044.html
- https://kb.isc.org/docs/cve-2020-8621
- https://security.gentoo.org/glsa/202008-19
- https://security.netapp.com/advisory/ntap-20200827-0003/
- https://usn.ubuntu.com/4468-1/
- https://www.synology.com/security/advisory/Synology_SA_20_19
