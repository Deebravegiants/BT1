# [H] CVE-2022-2320

## Summary
Severity: High
Advisory: CVE-2022-2320
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-09-01
Source: https://osv.dev/vulnerability/CVE-2022-2320
Type: osv

## Details
A flaw was found in the Xorg-x11-server. The specific flaw exists within the handling of ProcXkbSetDeviceInfo requests. The issue results from the lack of proper validation of user-supplied data, which can result in a memory access past the end of an allocated buffer. This flaw allows an attacker to escalate privileges and execute arbitrary code in the context of root.

## References
- https://security.gentoo.org/glsa/202210-30
- https://security.netapp.com/advisory/ntap-20221104-0003/
- https://www.zerodayinitiative.com/advisories/ZDI-22-963/
- https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/938
- https://gitlab.freedesktop.org/xorg/xserver/-/merge_requests/939
- https://lists.freedesktop.org/archives/xorg-announce/2022-July/003192.html
- https://github.com/freedesktop/xorg-xserver/commit/dd8caf39e9e15d8f302e54045dd08d8ebf1025dc
