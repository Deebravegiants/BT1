# [H] CVE-2021-3139

## Summary
Severity: High
Advisory: CVE-2021-3139
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2021-01-13
Source: https://osv.dev/vulnerability/CVE-2021-3139
Type: osv

## Details
In Open-iSCSI tcmu-runner 1.3.x, 1.4.x, and 1.5.x through 1.5.2, xcopy_locate_udev in tcmur_cmd_handler.c lacks a check for transport-layer restrictions, allowing remote attackers to read or write files via directory traversal in an XCOPY request. For example, an attack can occur over a network if the attacker has access to one iSCSI LUN. NOTE: relative to CVE-2020-28374, this is a similar mistake in a different algorithm.

## References
- http://www.openwall.com/lists/oss-security/2021/01/13/5
- https://www.openwall.com/lists/oss-security/2021/01/12/12
- https://bugzilla.suse.com/attachment.cgi?id=844938
- https://bugzilla.suse.com/show_bug.cgi?id=1178372
- https://github.com/open-iscsi/tcmu-runner/pull/644
