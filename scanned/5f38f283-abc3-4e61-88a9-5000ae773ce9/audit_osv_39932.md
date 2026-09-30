# [H] KanaDojo < 0.1.18 Command Injection via patchNotesData.json in release.yml

## Summary
Severity: High
Advisory: CVE-2026-48547
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-48547
Type: osv

## Details
KanaDojo contains a command injection vulnerability that allows an attacker with pull request access to execute arbitrary shell commands by inserting shell metacharacters into the version or changes fields of patchNotesData.json, which are interpolated unsanitized into a child_process.execSync() call in the release.yml workflow. Attackers can have a malicious pull request merged to trigger the GitHub Actions runner with contents write permissions and access to GITHUB_TOKEN.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48547.json
- https://github.com/lingdojo/kana-dojo/releases/tag/v0.1.18
- https://nvd.nist.gov/vuln/detail/CVE-2026-48547
- https://github.com/lingdojo/kana-dojo/commit/31b85a5d7c4b323ddeba3b2dc5e7807558710544
- https://github.com/lingdojo/kana-dojo
