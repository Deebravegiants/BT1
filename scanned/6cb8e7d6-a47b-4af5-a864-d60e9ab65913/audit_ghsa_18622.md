# [H] Flowise: Authenticated Command Execution and Sandbox Bypass via Puppeteer and Playwright Packages

## Summary
Severity: High
Advisory: GHSA-r4hh-pcgx-j5r2
CVE: CVE-2025-34267
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:L/VA:L/SC:H/SI:H/SA:L (CVSS_V4)
Published: 2025-10-14
Source: https://github.com/advisories/GHSA-r4hh-pcgx-j5r2
Type: github-advisory

## Affected
- npm: `flowise` — affected >=3.0.1 <3.0.8

## Details
Flowise v3.0.1 < 3.0.8 and all versions after with 'ALLOW_BUILTIN_DEP' enabled contain an authenticated remote code execution vulnerability and node VM sandbox escape due to insecure use of integrated modules (Puppeteer and Playwright) within the nodevm execution environment. An authenticated attacker able to create or run a tool that leverages Puppeteer/Playwright can specify attacker-controlled browser binary paths and parameters. When the tool executes, the attacker-controlled executable/parameters are run on the host and circumvent the intended nodevm sandbox restrictions, resulting in execution of arbitrary code in the context of the host.

**NOTE**: This vulnerability was incorrectly assigned as a duplicate CVE-2025-26319 and should be considered distinct from that identifier.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5w3r-f6gm-c25w
- https://nvd.nist.gov/vuln/detail/CVE-2025-34267
- https://github.com/FlowiseAI/Flowise/pull/5231
- https://flowiseai.com
- https://github.com/FlowiseAI/Flowise
- https://www.vulncheck.com/advisories/flowise-auth-command-execution-and-sandbox-bypass-via-puppeteer-and-playwright-packages
