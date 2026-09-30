# [H] Flowise OverrideConfig security vulnerability

## Summary
Severity: High
Advisory: GHSA-5cph-wvm9-45gj
CWE: CWE-15
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-21
Source: https://github.com/advisories/GHSA-5cph-wvm9-45gj
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <2.1.4

## Details
### Impact
Flowise allows developers to inject configuration into the Chainflow during execution through the `overrideConfig` option. This is supported in both the frontend web integration and the backend Prediction API. 

This has a range of fundamental issues that are a **major** security vulnerability. 
While this feature is intentional, it should have strong protections added and be disabled by default. 

These issues include: 
1. Remote code execution. While inside a sandbox this allows for
  1. Sandbox escape 
  2. DoS by crashing the server
  3. SSRF
2. Prompt Injection, both System and User
  1. Full control over LLM prompts
  2. Server variable and data exfiltration
And many many more such as altering the flow of a conversation, prompt exfiltration via LLM proxying etc.

These issues are self-targeted and do not persist to other users but do leave the server and business exposed. 
All issues are shown with the API but also work with the web embed.

### Workarounds
- `overrideConfig` should be disabled by default
- `overrideConfig` should have an explicit allow list of variables that are allowed to be modified. This way the user opts-in to where modifications can be made. 
- `vm2` and any forks of it should be removed as in the authors own words, "fixing the vulnerability seems impossible". The recommended replacement is https://www.npmjs.com/package/isolated-vm

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-5cph-wvm9-45gj
- https://github.com/FlowiseAI/Flowise
