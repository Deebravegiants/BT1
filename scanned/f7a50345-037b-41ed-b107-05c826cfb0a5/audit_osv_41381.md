# [M] SiYuan: Incomplete IsSensitivePath denylist: globalCopyFiles reads home-dir credential dotfiles into the workspace

## Summary
Severity: Medium
Advisory: CVE-2026-59854
Aliases: GHSA-vmm8-3ccv-ppvw
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-09
Source: https://osv.dev/vulnerability/CVE-2026-59854
Type: osv

## Details
SiYuan is an open-source personal knowledge management system. Prior to 3.7.1, POST /api/file/globalCopyFiles accepts attacker-supplied absolute source paths and relies on util.IsSensitivePath in kernel/util/path.go, whose denylist misses common home-directory credential files such as .git-credentials, .netrc, .pgpass, .kube/config, .docker/config.json, and .gnupg, allowing an authenticated administrator or API-token user to copy those files into the workspace and exfiltrate them through the file API. This issue is fixed in versions 3.7.1-alpha.2 and 3.7.1.

## References
- https://github.com/siyuan-note/siyuan/releases/tag/v3.7.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59854.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vmm8-3ccv-ppvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-59854
- https://github.com/siyuan-note/siyuan/commit/914c5180a88d17f6d38716a56483327b367ef55f
- https://github.com/siyuan-note/siyuan/commit/b54fee401799d987d2fd2888220938ad599b8c5e
