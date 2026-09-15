# [M] CVE-2018-16852

## Summary
Severity: Medium
Advisory: CVE-2018-16852
CVSS: 4.4 (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-11-28
Source: https://osv.dev/vulnerability/CVE-2018-16852
Type: osv

## Details
Samba from version 4.9.0 and before version 4.9.3 is vulnerable to a NULL pointer de-reference. During the processing of an DNS zone in the DNS management DCE/RPC server, the internal DNS server or the Samba DLZ plugin for BIND9, if the DSPROPERTY_ZONE_MASTER_SERVERS property or DSPROPERTY_ZONE_SCAVENGING_SERVERS property is set, the server will follow a NULL pointer and terminate. There is no further vulnerability associated with this issue, merely a denial of service.

## References
- http://www.securityfocus.com/bid/106024
- https://security.gentoo.org/glsa/202003-52
- https://security.netapp.com/advisory/ntap-20181127-0001/
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16852
- https://www.samba.org/samba/security/CVE-2018-16852.html
