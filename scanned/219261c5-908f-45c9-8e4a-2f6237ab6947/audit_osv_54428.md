# [H] CVE-2023-6185

## Summary
Severity: High
Advisory: CVE-2023-6185
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-12-11
Source: https://osv.dev/vulnerability/CVE-2023-6185
Type: osv

## Details
Improper Input Validation vulnerability in GStreamer integration of The Document Foundation LibreOffice allows an attacker to execute arbitrary GStreamer plugins.

In affected versions the filename of the embedded video is not sufficiently escaped when passed to GStreamer enabling an attacker to run arbitrary gstreamer plugins depending on what plugins are installed on the target system.

## References
- https://lists.debian.org/debian-lts-announce/2023/12/msg00026.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QB7UB6CTWQUDOE657OVVRSDYUY3IPBJG/
- https://www.debian.org/security/2023/dsa-5574
- https://www.libreoffice.org/about-us/security/advisories/cve-2023-6185
