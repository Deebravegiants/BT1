# [H] CVE-2020-14400

## Summary
Severity: High
Advisory: CVE-2020-14400
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-17
Source: https://osv.dev/vulnerability/CVE-2020-14400
Type: osv

## Details
An issue was discovered in LibVNCServer before 0.9.13. Byte-aligned data is accessed through uint16_t pointers in libvncserver/translate.c. NOTE: Third parties do not consider this to be a vulnerability as there is no known path of exploitation or cross of a trust boundary

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00033.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00055.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00066.html
- https://github.com/LibVNC/libvncserver/compare/LibVNCServer-0.9.12...LibVNCServer-0.9.13
- https://lists.debian.org/debian-lts-announce/2020/06/msg00035.html
- https://lists.debian.org/debian-lts-announce/2020/08/msg00045.html
- https://usn.ubuntu.com/4434-1/
- https://bugzilla.redhat.com/show_bug.cgi?id=1860361
- https://github.com/LibVNC/libvncserver/commit/53073c8d7e232151ea2ecd8a1243124121e10e2d
