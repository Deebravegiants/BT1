# [C] n8n vulnerable to Remote Code Execution via Git Node Custom Pre-Commit Hook

## Summary
Severity: Critical
Advisory: GHSA-wpqc-h9wp-chmq
CVE: CVE-2025-65964
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2025-12-08
Source: https://github.com/advisories/GHSA-wpqc-h9wp-chmq
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0.123.1 <1.119.2

## Details
### Impact

The n8n Git node allows workflows to set arbitrary Git configuration values through the _Add Config_ operation. When an attacker-controlled workflow sets `core.hooksPath` to a directory within the cloned repository containing a Git hook such as `pre-commit`, Git executes that hook during subsequent Git operations. Because Git hooks run as local system commands, this behavior can lead to **arbitrary command execution** on the underlying n8n host.

Successful exploitation requires the ability to create or modify an n8n workflow that uses the Git node.

Affected versions: **≥ 0.123.1 and < 1.119.2**

### Patches

This issue has been patched in **n8n version 1.119.2**.

All users running affected versions should upgrade to **1.119.2 or later**.

### Workarounds

If upgrading is not immediately possible, the following mitigations can reduce exposure:

- Exclude the Git node ([Docs](https://n8n-docs.teamlab.info/hosting/securing/blocking-nodes/#exclude-nodes)).
- Avoid cloning or interacting with untrusted repositories using the Git Node.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-wpqc-h9wp-chmq
- https://nvd.nist.gov/vuln/detail/CVE-2025-65964
- https://github.com/n8n-io/n8n/commit/d5a1171f95f75def5c3ac577707ab913e22aef04
- https://github.com/n8n-io/n8n
- https://github.com/n8n-io/n8n/releases/tag/n8n%401.119.2
- https://n8n-docs.teamlab.info/hosting/securing/blocking-nodes/#exclude-nodes
