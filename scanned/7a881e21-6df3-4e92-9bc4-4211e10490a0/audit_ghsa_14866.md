# [C] vanna vulnerable to remote code execution caused by prompt injection

## Summary
Severity: Critical
Advisory: GHSA-rrqq-fv6m-692m
CVE: CVE-2024-5826
CWE: CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-27
Source: https://github.com/advisories/GHSA-rrqq-fv6m-692m
Type: github-advisory

## Affected
- PyPI: `vanna` — affected >=0

## Details
In the latest version of vanna-ai/vanna, the `vanna.ask` function is vulnerable to remote code execution due to prompt injection. The root cause is the lack of a sandbox when executing LLM-generated code, allowing an attacker to manipulate the code executed by the `exec` function in `src/vanna/base/base.py`. This vulnerability can be exploited by an attacker to achieve remote code execution on the app backend server, potentially gaining full control of the server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5826
- https://github.com/vanna-ai/vanna
- https://huntr.com/bounties/90620087-44ac-4e43-b659-3c5d30889369
