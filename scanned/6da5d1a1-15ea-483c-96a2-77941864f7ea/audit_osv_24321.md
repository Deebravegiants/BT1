# [H] CVE-2023-0494

## Summary
Severity: High
Advisory: CVE-2023-0494
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-27
Source: https://osv.dev/vulnerability/CVE-2023-0494
Type: osv

## Details
A vulnerability was found in X.Org. This issue occurs due to a dangling pointer in DeepCopyPointerClasses that can be exploited by ProcXkbSetDeviceInfo() and ProcXkbGetDeviceInfo() to read and write into freed memory. This can lead to local privilege elevation on systems where the X server runs privileged and remote code execution for ssh X forwarding sessions.

## References
- https://lists.x.org/archives/xorg-announce/2023-February/003320.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0494.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0494
- https://security.gentoo.org/glsa/202305-30
- https://bugzilla.redhat.com/show_bug.cgi?id=2165995
- https://gitlab.freedesktop.org/xorg/xserver/-/commit/0ba6d8c37071131a49790243cdac55392ecf71ec
