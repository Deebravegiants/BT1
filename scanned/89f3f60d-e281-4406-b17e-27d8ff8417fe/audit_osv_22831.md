# [M] Division by zero in urbdrc channel in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2022-39318
Aliases: GHSA-387j-8j96-7q35
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-16
Source: https://osv.dev/vulnerability/CVE-2022-39318
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. Affected versions of FreeRDP are missing input validation in `urbdrc` channel. A malicious server can trick a FreeRDP based client to crash with division by zero. This issue has been addressed in version 2.9.0. All users are advised to upgrade. Users unable to upgrade should not use the `/usb` redirection switch.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39318.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-387j-8j96-7q35
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGQN3OWQNHSMWKOF4D35PF5ASKNLC74B/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39318
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/80adde17ddc4b596ed1dae0922a0c54ab3d4b8ea
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
