# [H] CVE-2020-10699

## Summary
Severity: High
Advisory: CVE-2020-10699
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-15
Source: https://osv.dev/vulnerability/CVE-2020-10699
Type: osv

## Details
A flaw was found in Linux, in targetcli-fb versions 2.1.50 and 2.1.51 where the socket used by targetclid was world-writable. If a system enables the targetclid socket, a local attacker can use this flaw to modify the iSCSI configuration and escalate their privileges to root.

## References
- https://github.com/open-iscsi/targetcli-fb/issues/162
- https://security.gentoo.org/glsa/202008-22
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2020-10699
