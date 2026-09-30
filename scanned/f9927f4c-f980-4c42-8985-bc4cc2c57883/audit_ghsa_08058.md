# [C] n8n Vulnerable to Command Injection in Community Package Installation

## Summary
Severity: Critical
Advisory: GHSA-7c4h-vh2m-743m
CVE: CVE-2026-21893
CWE: CWE-20, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-7c4h-vh2m-743m
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0.187.0 <1.120.3

## Details
### Impact
A Command Injection vulnerability was identified in n8n’s community package installation functionality. The issue allowed authenticated users with administrative permissions to execute arbitrary system commands on the n8n host under specific conditions.

**Important context**

- Exploitation requires _administrative_ access to the n8n instance.
- The affected functionality is restricted to trusted users who are already permitted to install third-party community packages.
- No unauthenticated or low-privilege exploitation is possible.
- There is no evidence of exploitation in the wild.

Because administrative users can already extend n8n with custom or community code, the vulnerability does not meaningfully expand the threat model beyond existing administrator capabilities. However, it represents a violation of secure coding practices and has therefore been addressed.

### Patches
Users are advised to upgrade to n8n version 1.120.3 or later, which fully resolves the issue.

As a general security best practice, n8n instance owners should ensure that:
- Administrative access is limited to trusted users only.
- Community packages are installed only from trusted sources.
- Instances are kept up to date with the latest security releases.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-7c4h-vh2m-743m
- https://nvd.nist.gov/vuln/detail/CVE-2026-21893
- https://github.com/n8n-io/n8n/commit/ae0669a736cc496beeb296e115267862727ae838
- https://github.com/n8n-io/n8n
