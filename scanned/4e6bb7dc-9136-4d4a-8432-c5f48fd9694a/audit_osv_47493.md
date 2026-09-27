# [H] CVE-2016-7039

## Summary
Severity: High
Advisory: CVE-2016-7039
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-16
Source: https://osv.dev/vulnerability/CVE-2016-7039
Type: osv

## Details
The IP stack in the Linux kernel through 4.8.2 allows remote attackers to cause a denial of service (stack consumption and panic) or possibly have unspecified other impact by triggering use of the GRO path for large crafted packets, as demonstrated by packets that contain only VLAN headers, a related issue to CVE-2016-8666.

## References
- http://rhn.redhat.com/errata/RHSA-2016-2047.html
- http://www.securityfocus.com/bid/93476
- https://access.redhat.com/errata/RHSA-2017:0372
- https://bto.bluecoat.com/security-advisory/sa134
- http://rhn.redhat.com/errata/RHSA-2016-2107.html
- http://rhn.redhat.com/errata/RHSA-2016-2110.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinoct2016-3090545.html
- http://www.oracle.com/technetwork/topics/security/ovmbulletinoct2016-3090547.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1375944
- http://www.openwall.com/lists/oss-security/2016/10/10/15
- https://patchwork.ozlabs.org/patch/680412/
