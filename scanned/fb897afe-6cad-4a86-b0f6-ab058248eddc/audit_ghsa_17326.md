# [C] MCP Watch has a Critical Command Injection in cloneRepo allows Remote Code Execution (RCE) via malicious URL

## Summary
Severity: Critical
Advisory: GHSA-27m7-ffhq-jqrm
CVE: CVE-2025-66401
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-27m7-ffhq-jqrm
Type: github-advisory

## Affected
- npm: `mcp-watch` — affected >=0

## Details
### Summary
The `MCPScanner ` class contains a critical Command Injection vulnerability in the `cloneRepo `method. The application passes the user-supplied githubUrl argument directly to a system shell via execSync without sanitization. This allows an attacker to execute arbitrary commands on the host machine by appending shell metacharacters to the URL.

### Details
The vulnerability exists in the src/scanner/MCPScanner.ts file within the cloneRepo method.

[https://github.com/kapilduraphe/mcp-watch/blob/0fca7228bd313ae5aa938d61311377e88ce6e682/src/scanner/McpScanner.ts#L181](https://github.com/kapilduraphe/mcp-watch/blob/0fca7228bd313ae5aa938d61311377e88ce6e682/src/scanner/McpScanner.ts#L181)

The code uses child_process.execSync to execute a git clone command:

Because execSync spawns a shell (defaulting to `/bin/sh` on Unix or` cmd.exe` on Windows), any shell metacharacters present in the url argument will be interpreted by the shell. The application does not validate that the url is a valid Git URL, nor does it sanitize input for shell metacharacters.

### PoC
Install the package or clone the repository.

Run the scanner using the CLI (or invoke scanRepository programmatically).

Provide a malicious URL containing a command separator (e.g., ;, &, or |) and a system command.
payload : `npm run scan:github "https://github.com/kapilduraphe/mcp-watch & calc.exe"`

<img width="1918" height="1046" alt="image" src="https://github.com/user-attachments/assets/021c1dfa-3f87-483c-aecb-6939bcf9c925" />



### Impact
Severity: **Critical**

**CVSS Score**: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Description: This vulnerability allows an attacker to execute arbitrary code on the machine running the scanner.

If run by a developer locally, it compromises their workstation.

If deployed as a hosted scanning service, it grants the attacker full control over the server (RCE), leading to potential data exfiltration, service disruption, or further lateral movement within the infrastructure.

**Context Dependent Risk:**

Local CLI : If you run this tool locally on your own machine, you are "hacking yourself." The risk is limited unless you copy-paste a malicious URL sent by someone else (e.g., "Hey, check this repo scan: npm run scan "https://git./..; rm -rf /").

**Web Service / CI Pipeline (Critical Risk)**: If this scanner is deployed as a web service (e.g., "Paste your repo URL to scan"), an attacker can take full control of the server immediately.

## References
- https://github.com/kapilduraphe/mcp-watch/security/advisories/GHSA-27m7-ffhq-jqrm
- https://nvd.nist.gov/vuln/detail/CVE-2025-66401
- https://github.com/kapilduraphe/mcp-watch/commit/e7da78c5b4b960f8b66c254059ad9ebc544a91a6
- https://github.com/kapilduraphe/mcp-watch
