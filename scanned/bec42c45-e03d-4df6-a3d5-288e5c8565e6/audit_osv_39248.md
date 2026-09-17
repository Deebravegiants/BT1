# [M] Vowpal Wabbit: Shell injection via crafted PR title in python_checks.yml allows arbitrary command execution on CI runner

## Summary
Severity: Medium
Advisory: CVE-2026-44723
Aliases: GHSA-cg2g-xgg7-3xxq
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-05-26
Source: https://osv.dev/vulnerability/CVE-2026-44723
Type: osv

## Details
Vowpal Wabbit is a machine learning system. The workflow .github/workflows/python_checks.yml embeds ${{ github.event.pull_request.title }} directly inside double-quoted bash strings in four separate steps across four jobs, each passing it as a CLI argument to the Python test script run_tests_model_gen_and_load.py. The shell interprets the expanded string before invoking Python, allowing an attacker to break out of the quotes and execute arbitrary commands on the runner. The pull_request trigger fires on PRs targeting any branch (branches: ['*']), with no additional access gate. This vulnerability is fixed by the 998e390e80a7e8192d7849b7784bc113dbd190ad commit.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44723.json
- https://github.com/VowpalWabbit/vowpal_wabbit/security/advisories/GHSA-cg2g-xgg7-3xxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44723
- https://github.com/VowpalWabbit/vowpal_wabbit/commit/998e390e80a7e8192d7849b7784bc113dbd190ad
