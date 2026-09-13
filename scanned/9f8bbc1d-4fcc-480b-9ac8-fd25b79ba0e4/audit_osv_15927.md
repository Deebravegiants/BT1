# [C] CVE-2019-20788

## Summary
Severity: Critical
Advisory: CVE-2019-20788
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-23
Source: https://osv.dev/vulnerability/CVE-2019-20788
Type: osv

## Details
libvncclient/cursor.c in LibVNCServer through 0.9.12 has a HandleCursorShape integer overflow and heap-based buffer overflow via a large height or width value. NOTE: this may overlap CVE-2019-15690.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00027.html
- https://usn.ubuntu.com/4407-1/
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://github.com/LibVNC/libvncserver/commit/54220248886b5001fbbb9fa73c4e1a2cb9413fed
- https://securitylab.github.com/advisories/GHSL-2020-064-libvnc-libvncclient
