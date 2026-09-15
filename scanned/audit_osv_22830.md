# [M] Out of bounds read in zgfx decoder in FreeRDP

## Summary
Severity: Medium
Advisory: CVE-2022-39317
Aliases: GHSA-99cm-4gw7-c8jh
CVSS: 4.6 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:L/A:L)
Published: 2022-11-16
Source: https://osv.dev/vulnerability/CVE-2022-39317
Type: osv

## Details
FreeRDP is a free remote desktop protocol library and clients. Affected versions of FreeRDP are missing a range check for input offset index in ZGFX decoder. A malicious server can trick a FreeRDP based client to read out of bound data and try to decode it. This issue has been addressed in version 2.9.0. There are no known workarounds for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39317.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-99cm-4gw7-c8jh
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDOTAOJBCZKREZJPT6VZ25GESI5T6RBG/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGQN3OWQNHSMWKOF4D35PF5ASKNLC74B/
- https://nvd.nist.gov/vuln/detail/CVE-2022-39317
- https://security.gentoo.org/glsa/202401-16
