# [C] Flowise Sandbox Escape to RCE

## Summary
Severity: Critical
Advisory: CVE-2026-69253
Aliases: GHSA-wg86-r78f-74mp
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-69253
Type: osv

## Details
Flowise is a drag-and-drop user interface for building customized large language model (LLM) flows. Prior to version 3.1.3, several custom-tool components — AgentAsTool, ChatflowTool, and ExecuteFlow — ran code in the in-process  vm2  sandbox. To build that code, they inserted a user-controlled  baseURL  value straight into the JavaScript source, for example  const url = "${baseURL}/..."; . The only check on  baseURL  was  isValidURL , but a valid-looking URL can still contain characters that break out of a code string. An authenticated user could craft a  baseURL  that passed this check, closed the surrounding string, and injected their own JavaScript into the sandboxed script (code injection, CWE-94). The  vm2  sandbox runs in the same Node.js process as Flowise and exposes risky dependencies. As a result, the injected code could escape the sandbox and run arbitrary code on the Flowise server as the Flowise process user. Exploitation only requires an authenticated session. The issue is fixed in version 3.1.3, which passes the URL to the sandbox as data instead of inserting it into code and adds stricter URL validation.

## References
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise@3.1.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/69xxx/CVE-2026-69253.json
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-wg86-r78f-74mp
- https://nvd.nist.gov/vuln/detail/CVE-2026-69253
- https://github.com/FlowiseAI/Flowise/commit/3f257bdc8196082a178da7134a075824401b13b9
- https://github.com/FlowiseAI/Flowise/pull/6417
