# [C] AutoGPT bypass of the shell commands denylist settings

## Summary
Severity: Critical
Advisory: GHSA-g84q-54hf-36rg
CVE: CVE-2024-6091
CWE: CWE-78
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-g84q-54hf-36rg
Type: github-advisory

## Affected
- PyPI: `agpt` — affected >=0

## Details
A vulnerability in significant-gravitas/autogpt version 0.5.1 allows an attacker to bypass the shell commands denylist settings. The issue arises when the denylist is configured to block specific commands, such as `whoami` and `/bin/whoami`. An attacker can circumvent this restriction by executing commands with a modified path, such as `/bin/./whoami`, which is not recognized by the denylist.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6091
- https://github.com/significant-gravitas/autogpt/commit/ef691359b774a1f9f80cf4f5ace9821967b718ed
- https://github.com/Significant-Gravitas/AutoGPT
- https://huntr.com/bounties/8a742c13-bb5e-4bc9-8b86-049d8a386050
