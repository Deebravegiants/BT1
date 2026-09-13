# [H] rtk: Permission-gate bypass in rtk rewrite auto-allow via unsplit shell separators

## Summary
Severity: High
Advisory: CVE-2026-54555
Aliases: GHSA-7gxq-fvfc-g327
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-23
Source: https://osv.dev/vulnerability/CVE-2026-54555
Type: osv

## Details
rtk filters and compresses command outputs before they reach your LLM context. Prior to 0.42.2, the permission splitter did not conservatively split or reject several shell constructs that Bash treats as command execution boundaries or nested execution. As a result, a command beginning with an allowed prefix such as git could hide a second command behind one of these constructs. rtk rewrite returned exit code 0, causing the Claude hook to emit permissionDecision: "allow". The rewritten command still contained the hidden command, so it ran without the user confirmation or denial that the permission rules were intended to enforce. This vulnerability is fixed in 0.42.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54555.json
- https://github.com/rtk-ai/rtk/security/advisories/GHSA-7gxq-fvfc-g327
- https://nvd.nist.gov/vuln/detail/CVE-2026-54555
