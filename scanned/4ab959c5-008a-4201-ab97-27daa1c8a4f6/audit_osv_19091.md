# [H] CVE-2020-7216

## Summary
Severity: High
Advisory: CVE-2020-7216
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-02-05
Source: https://osv.dev/vulnerability/CVE-2020-7216
Type: osv

## Details
An ni_dhcp4_parse_response memory leak in openSUSE wicked 0.6.55 and earlier allows network attackers to cause a denial of service by sending DHCP4 packets without a message type option.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00005.html
- https://bugzilla.suse.com/show_bug.cgi?id=1160905
