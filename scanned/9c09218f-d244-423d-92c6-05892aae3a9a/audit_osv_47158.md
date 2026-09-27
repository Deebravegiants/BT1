# [M] CVE-2016-0756

## Summary
Severity: Medium
Advisory: CVE-2016-0756
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2016-0756
Type: osv

## Details
The generate_dialback function in the mod_dialback module in Prosody before 0.9.10 does not properly separate fields when generating dialback keys, which allows remote attackers to spoof XMPP network domains via a crafted stream id and domain name that is included in the target domain as a suffix.

## References
- http://www.openwall.com/lists/oss-security/2016/01/27/10
- http://www.securityfocus.com/bid/82241
- https://prosody.im/issues/issue/596
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176796.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-February/176914.html
- https://prosody.im/security/advisory_20160127/
- http://www.debian.org/security/2016/dsa-3463
- http://blog.prosody.im/prosody-0-9-10-released/
