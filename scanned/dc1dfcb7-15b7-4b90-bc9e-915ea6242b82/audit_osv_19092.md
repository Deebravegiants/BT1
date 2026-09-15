# [H] CVE-2020-7217

## Summary
Severity: High
Advisory: CVE-2020-7217
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-11
Source: https://osv.dev/vulnerability/CVE-2020-7217
Type: osv

## Details
An ni_dhcp4_fsm_process_dhcp4_packet memory leak in openSUSE wicked 0.6.55 and earlier allows network attackers to cause a denial of service by sending DHCP4 packets with a different client-id.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00011.html
- https://github.com/openSUSE/wicked/releases
- https://www.suse.com/security/cve/CVE-2020-7217/
- https://bugzilla.suse.com/show_bug.cgi?id=1160906
