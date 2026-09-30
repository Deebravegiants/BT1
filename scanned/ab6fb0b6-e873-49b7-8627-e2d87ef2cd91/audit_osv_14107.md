# [C] CVE-2018-7226

## Summary
Severity: Critical
Advisory: CVE-2018-7226
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-19
Source: https://osv.dev/vulnerability/CVE-2018-7226
Type: osv

## Details
An issue was discovered in vcSetXCutTextProc() in VNConsole.c in LinuxVNC and VNCommand from the LibVNC/vncterm distribution through 0.9.10. Missing sanitization of the client-specified message length may cause integer overflow or possibly have unspecified other impact via a specially crafted VNC packet.

## References
- https://security.gentoo.org/glsa/201908-05
- https://github.com/LibVNC/vncterm/issues/6
- http://openwall.com/lists/oss-security/2018/02/18/2
