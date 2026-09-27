# [C] Mistral Vibe < 2.23.3 Arbitrary Command Execution via git fsmonitor Hook

## Summary
Severity: Critical
Advisory: CVE-2026-67623
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-67623
Type: osv

## Details
Mistral Vibe before 2.23.3 contains a remote code execution vulnerability that allows attackers to execute arbitrary commands by embedding a malicious core.fsmonitor hook in a repository's .git/config file, which is triggered when vibe invokes git status --porcelain without suppressing hook execution. Attackers can distribute or create a crafted repository containing a malicious fsmonitor entry to achieve arbitrary command execution with the victim's full privileges when any vibe command is run inside that repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67623.json
- https://github.com/mistralai/mistral-vibe/releases/tag/v2.23.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-67623
- https://www.vulncheck.com/advisories/mistral-vibe-arbitrary-command-execution-via-git-fsmonitor-hook
- https://github.com/mistralai/mistral-vibe/pull/962
- https://github.com/mistralai/mistral-vibe/pull/978
- https://github.com/mistralai/mistral-vibe/commit/68ff32e6a92e80a874c8153312f0aa8ae4955477
- https://github.com/mistralai/mistral-vibe
- https://github.com/mistralai/mistral-vibe/issues/942
- https://therealcoiffeur.com/c111011.html
