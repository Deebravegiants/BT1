# [M] Missing length validation in urbdrc channel in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2022-39319
Aliases: GHSA-mvxm-wfj2-5fvh
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-11-16
Source: https://osv.dev/vulnerability/CVE-2022-39319
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. Affected versions of FreeRDP are missing input length validation in the `urbdrc` channel. A malicious server can trick a FreeRDP based client to read out of bound data and send it back to the server. This issue has been addressed in version 2.9.0 and all users are advised to upgrade. Users unable to upgrade should not use the `/usb` redirection switch.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39319.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-mvxm-wfj2-5fvh
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGQN3OWQNHSMWKOF4D35PF5ASKNLC74B/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39319
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/11555828d2cf289b350baba5ad1f462f10b80b76
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
