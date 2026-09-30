# [H] CVE-2022-46342

## Summary
Severity: High
Advisory: CVE-2022-46342
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-46342
Type: osv

## Details
A vulnerability was found in X.Org. This security flaw occurs because the handler for the XvdiSelectVideoNotify request may write to memory after it has been freed. This issue can lead to local privileges elevation on systems where the X se

## References
- https://access.redhat.com/security/cve/CVE-2022-46342
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5NELB7YDWRABYYBG4UPTHRBDTKJRV5M2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DXDF2O5PPLE3SVAJJYUOSAD5QZ4TWQ2G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/Z67QC4C3I2FI2WRFIUPEHKC36J362MLA/
- https://security.gentoo.org/glsa/202305-30
- https://www.debian.org/security/2022/dsa-5304
- https://bugzilla.redhat.com/show_bug.cgi?id=2151757
