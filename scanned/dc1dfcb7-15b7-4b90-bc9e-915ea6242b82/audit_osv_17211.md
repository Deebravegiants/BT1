# [M] CVE-2020-13775

## Summary
Severity: Medium
Advisory: CVE-2020-13775
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-02
Source: https://osv.dev/vulnerability/CVE-2020-13775
Type: osv

## Details
ZNC 1.8.0 up to 1.8.1-rc1 allows authenticated users to trigger an application crash (with a NULL pointer dereference) if echo-message is not enabled and there is no network.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DNVBE4T2DRJRQHFRMHYBTN4OSOL6DBHR/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HS3DWGXLVRROQQA57UIPMDM6XMVEMBRA/
- https://github.com/znc/znc/commit/2390ad111bde16a78c98ac44572090b33c3bd2d8
- https://github.com/znc/znc/commit/d229761821da38d984a9e4098ad96842490dc001
