# [H] CVE-2016-2821

## Summary
Severity: High
Advisory: CVE-2016-2821
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2016-06-13
Source: https://osv.dev/vulnerability/CVE-2016-2821
Type: osv

## Details
Use-after-free vulnerability in the mozilla::dom::Element class in Mozilla Firefox before 47.0 and Firefox ESR 45.x before 45.2, when contenteditable mode is enabled, allows remote attackers to execute arbitrary code or cause a denial of service (heap memory corruption) by triggering deletion of DOM elements that were created in the editor.

## References
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00016.html
- http://lists.opensuse.org/opensuse-security-announce/2016-06/msg00055.html
- http://www.oracle.com/technetwork/topics/security/linuxbulletinapr2016-2952096.html
- http://www.securityfocus.com/bid/91075
- http://www.securitytracker.com/id/1036057
- http://www.debian.org/security/2016/dsa-3600
- https://access.redhat.com/errata/RHSA-2016:1217
- http://www.mozilla.org/security/announce/2016/mfsa2016-51.html
- http://www.ubuntu.com/usn/USN-2993-1
- https://bugzilla.mozilla.org/show_bug.cgi?id=1271460
