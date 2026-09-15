# [C] @akoskm/create-mcp-server-stdio is vulnerable to MCP Server Command Injection through `exec` API

## Summary
Severity: Critical
Advisory: GHSA-3ch2-jxxc-v4xf
CVE: CVE-2025-54994
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-3ch2-jxxc-v4xf
Type: github-advisory

## Affected
- npm: `@akoskm/create-mcp-server-stdio` — affected >=0 <0.0.13

## Details
# Command Injection in MCP Server

The MCP Server at https://github.com/akoskm/create-mcp-server-stdio is written in a way that is vulnerable to command injection vulnerability attacks as part of some of its MCP Server tool definition and implementation.

## Vulnerable tool

The MCP Server exposes the tool `which-app-on-port` which relies on Node.js child process API `exec` which is an unsafe and vulnerable API if concatenated with untrusted user input.

Vulnerable line of code: https://github.com/akoskm/create-mcp-server-stdio/blob/main/src/index.ts#L24-L40

```js
server.tool("which-app-on-port", { port: z.number() }, async ({ port }) => {
  const result = await new Promise<ProcessInfo>((resolve, reject) => {
    exec(`lsof -t -i tcp:${port}`, (error, pidStdout) => {
      if (error) {
        reject(error);
        return;
      }
      const pid = pidStdout.trim();
      exec(`ps -p ${pid} -o comm=`, (error, stdout) => {
        if (error) {
          reject(error);
          return;
        }
        resolve({ command: stdout.trim(), pid });
      });
    });
  });
```

## Exploitation

When LLMs are tricked through prompt injection (and other techniques and attack vectors) to call the tool with input that uses special shell characters such as `; rm -rf /tmp;#` (be careful actually executing this payload) and other payload variations, the full command-line text will be interepted by the shell and result in other commands except of `ps` executing on the host running the MCP Server.

Reference example from prior security research on this topic:

![Cursor defined MCP Server vulnerable to command injection](https://res.cloudinary.com/snyk/image/upload/f_auto,w_2560,q_auto/v1747081395/Screenshot_2025-05-07_at_9.22.11_AM_d76kvm.png)

## Impact

User initiated and remote command injection on a running MCP Server.

## Recommendation

- Don't use `exec`. Use `execFile` instead, which pins the command and provides the arguments as array elements.
- If the user input is not a command-line flag, use the `--` notation to terminate command and command-line flag, and indicate that the text after the `--` double dash notation is benign value.

## References and Prior work

1. [Exploiting MCP Servers Vulnerable to Command Injection](https://snyk.io/articles/exploiting-mcp-servers-vulnerable-to-command-injection/)
2. Liran's [Node.js Secure Coding: Defending Against Command Injection Vulnerabilities](https://www.nodejs-security.com/book/command-injection)

##

Disclosed by [Liran Tal](https://lirantal.com)

## References
- https://github.com/akoskm/create-mcp-server-stdio/security/advisories/GHSA-3ch2-jxxc-v4xf
- https://nvd.nist.gov/vuln/detail/CVE-2025-54994
- https://github.com/akoskm/create-mcp-server-stdio/pull/1
- https://github.com/akoskm/create-mcp-server-stdio/commit/48c26bbe1f8c62764e4592f33c8300d1cadd2eac
- https://github.com/akoskm/create-mcp-server-stdio
- https://github.com/akoskm/create-mcp-server-stdio/blob/main/src/index.ts#L24-L40
