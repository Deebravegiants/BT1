# [C] xygeni-action v5 tag poisoned with C2 backdoor

## Summary
Severity: Critical
Advisory: CVE-2026-31976
Aliases: GHSA-f8q5-h5qh-33mh
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31976
Type: osv

## Details
xygeni-action is the GitHub Action for Xygeni Scanner. On March 3, 2026, an attacker with access to compromised credentials created a series of pull requests (#46, #47, #48) injecting obfuscated shell code into action.yml. The PRs were blocked by branch protection rules and never merged into the main branch. However, the attacker used the compromised GitHub App credentials to move the mutable v5 tag to point at the malicious commit (4bf1d4e19ad81a3e8d4063755ae0f482dd3baf12) from one of the unmerged PRs. This commit remained in the repository's git object store, and any workflow referencing @v5 would fetch and execute it. This is a supply chain compromise via tag poisoning. Any GitHub Actions workflow referencing xygeni/xygeni-action@v5 during the affected window (approximately March 3–10, 2026) executed a C2 implant that granted the attacker arbitrary command execution on the CI runner for up to 180 seconds per workflow run.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31976.json
- https://github.com/xygeni/xygeni-action/security/advisories/GHSA-f8q5-h5qh-33mh
- https://nvd.nist.gov/vuln/detail/CVE-2026-31976
- https://github.com/xygeni/xygeni-action/issues/54
