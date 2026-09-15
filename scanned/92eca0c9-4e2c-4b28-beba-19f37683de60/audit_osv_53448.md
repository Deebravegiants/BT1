# [H] CVE-2022-4283

## Summary
Severity: High
Advisory: CVE-2022-4283
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-4283
Type: osv

## Details
A vulnerability was found in X.Org. This security flaw occurs because the XkbCopyNames function left a dangling pointer to freed memory, resulting in out-of-bounds memory access on subsequent XkbGetKbdByName requests.. This issue can lead to local privileges elevation on systems where the X server is running privileged and remote code execution for ssh X forwarding sessions.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5NELB7YDWRABYYBG4UPTHRBDTKJRV5M2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DXDF2O5PPLE3SVAJJYUOSAD5QZ4TWQ2G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z67QC4C3I2FI2WRFIUPEHKC36J362MLA/
- https://security.gentoo.org/glsa/202305-30
- https://www.debian.org/security/2022/dsa-5304
- https://access.redhat.com/security/cve/CVE-2022-4283
- https://bugzilla.redhat.com/show_bug.cgi?id=2151761
