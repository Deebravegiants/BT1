# [H] CVE-2023-5574

## Summary
Severity: High
Advisory: CVE-2023-5574
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-10-25
Source: https://osv.dev/vulnerability/CVE-2023-5574
Type: osv

## Details
A use-after-free flaw was found in xorg-x11-server-Xvfb. This issue occurs in Xvfb with a very specific and legacy configuration (a multi-screen setup with multiple protocol screens, also known as Zaphod mode). If the pointer is warped from a screen 1 to a screen 0, a use-after-free issue may be triggered during shutdown or reset of the Xvfb server, allowing for possible escalation of privileges or denial of service.

## References
- https://access.redhat.com/errata/RHSA-2024:2298
- https://access.redhat.com/security/cve/CVE-2023-5574
- https://security.netapp.com/advisory/ntap-20231130-0004/
- https://bugzilla.redhat.com/show_bug.cgi?id=2244735
- https://lists.x.org/archives/xorg-announce/2023-October/003430.html
