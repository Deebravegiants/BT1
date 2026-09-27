# [H] CVE-2019-15681

## Summary
Severity: High
Advisory: CVE-2019-15681
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-10-29
Source: https://osv.dev/vulnerability/CVE-2019-15681
Type: osv

## Details
LibVNC commit before d01e1bb4246323ba6fcee3b82ef1faa9b1dac82a contains a memory leak (CWE-655) in VNC server code, which allow an attacker to read stack memory and can be abused for information disclosure. Combined with another vulnerability, it can be used to leak stack memory and bypass ASLR. This attack appear to be exploitable via network connectivity. These vulnerabilities have been fixed in commit d01e1bb4246323ba6fcee3b82ef1faa9b1dac82a.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00027.html
- http://lists.opensuse.org/opensuse-security-announce/2020-07/msg00073.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-390195.pdf
- https://lists.debian.org/debian-lts-announce/2019/10/msg00039.html
- https://lists.debian.org/debian-lts-announce/2019/10/msg00042.html
- https://lists.debian.org/debian-lts-announce/2019/11/msg00032.html
- https://lists.debian.org/debian-lts-announce/2019/12/msg00028.html
- https://usn.ubuntu.com/4407-1/
- https://usn.ubuntu.com/4547-1/
- https://usn.ubuntu.com/4573-1/
- https://usn.ubuntu.com/4587-1/
- https://github.com/LibVNC/libvncserver/commit/d01e1bb4246323ba6fcee3b82ef1faa9b1dac82a
