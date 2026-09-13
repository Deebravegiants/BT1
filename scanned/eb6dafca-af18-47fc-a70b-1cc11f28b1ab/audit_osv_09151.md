# [H] CVE-2016-8637

## Summary
Severity: High
Advisory: CVE-2016-8637
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-08-01
Source: https://osv.dev/vulnerability/CVE-2016-8637
Type: osv

## Details
A local information disclosure issue was found in dracut before 045 when generating initramfs images with world-readable permissions when 'early cpio' is used, such as when including microcode updates. Local attacker can use this to obtain sensitive information from these files, such as encryption keys or credentials.

## References
- http://www.securityfocus.com/bid/94128
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2016-8637
- https://github.com/dracutdevs/dracut/commit/0db98910a11c12a454eac4c8e86dc7a7bbc764a4
- http://seclists.org/oss-sec/2016/q4/352
