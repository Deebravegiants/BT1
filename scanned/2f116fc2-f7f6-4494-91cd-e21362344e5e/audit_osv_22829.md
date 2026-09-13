# [M] Out of bound read in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2022-39316
Aliases: GHSA-5w4j-mrrh-jjrm
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-11-16
Source: https://osv.dev/vulnerability/CVE-2022-39316
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. In affected versions there is an out of bound read in ZGFX decoder component of FreeRDP. A malicious server can trick a FreeRDP based client to read out of bound data and try to decode it likely resulting in a crash. This issue has been addressed in the 2.9.0 release. Users are advised to upgrade.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39316.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-5w4j-mrrh-jjrm
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGQN3OWQNHSMWKOF4D35PF5ASKNLC74B/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39316
- https://security.gentoo.org/glsa/202401-16
- https://github.com/FreeRDP/FreeRDP/commit/e865c24efc40ebc52e75979c94cdd4ee2c1495b0
- https://lists.debian.org/debian-lts-announce/2023/11/msg00010.html
