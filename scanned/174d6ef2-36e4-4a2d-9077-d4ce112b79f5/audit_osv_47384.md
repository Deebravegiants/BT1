# [M] CVE-2016-4470

## Summary
Severity: Medium
Advisory: CVE-2016-4470
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-27
Source: https://osv.dev/vulnerability/CVE-2016-4470
Type: osv

## Details
The key_reject_and_link function in security/keys/key.c in the Linux kernel through 4.6.3 does not ensure that a certain data structure is initialized, which allows local users to cause a denial of service (system crash) via vectors involving a crafted keyctl request2 command.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00021.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00026.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00044.html
- http://www.openwall.com/lists/oss-security/2016/06/15/11
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00019.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00013.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00023.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00020.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00008.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00007.html
