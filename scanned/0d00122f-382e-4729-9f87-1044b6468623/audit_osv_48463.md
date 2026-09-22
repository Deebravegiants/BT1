# [M] CVE-2017-7829

## Summary
Severity: Medium
Advisory: CVE-2017-7829
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7829
Type: osv

## Details
It is possible to spoof the sender's email address and display an arbitrary sender address to the email recipient. The real sender's address is not displayed if preceded by a null character in the display string. This vulnerability affects Thunderbird < 52.5.2.

## References
- https://usn.ubuntu.com/3529-1/
- https://www.debian.org/security/2017/dsa-4075
- https://www.mozilla.org/security/advisories/mfsa2017-30/
- http://www.securityfocus.com/bid/102258
- http://www.securitytracker.com/id/1040123
- https://access.redhat.com/errata/RHSA-2018:0061
- https://lists.debian.org/debian-lts-announce/2017/12/msg00026.html
- https://bugzilla.mozilla.org/show_bug.cgi?id=1423432
