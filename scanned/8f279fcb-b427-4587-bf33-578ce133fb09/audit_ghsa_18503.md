# [H] GitHub Kanban MCP Server vulnerable to Command Injection

## Summary
Severity: High
Advisory: GHSA-6jx8-rcjx-vmwf
CVE: CVE-2025-53818
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-07-15
Source: https://github.com/advisories/GHSA-6jx8-rcjx-vmwf
Type: github-advisory

## Affected
- npm: `@sunwood-ai-labs/github-kanban-mcp-server` — affected >=0

## Details
The MCP Server at https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/ is written in a way that is vulnerable to command injection vulnerability attacks as part of some of its MCP Server tool definition and implementation.

## Vulnerable tool

The MCP Server exposes the tool `add_comment` which relies on Node.js child process API `exec` to execute the GitHub (`gh`) command, is an unsafe and vulnerable API if concatenated with untrusted user input.

Data flows from the tool definition [here](https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/main/src/handlers/tool-handlers.ts#L79) which takes in `args.issue_number` and calls `handleAddComment()` in [this definitino](https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/main/src/handlers/comment-handlers.ts#L8) that uses `exec` in an insecure way.

Vulnerable line of code: https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/main/src/handlers/comment-handlers.ts#L8-L23

```js
export async function handleAddComment(args: {
  repo: string;
  issue_number: string;
  body: string;
  state?: 'open' | 'closed';
}): Promise<ToolResponse> {
  const tempFile = 'comment_body.md';

  try {
    // ステータスの変更が指定されている場合は先に処理
    if (args.state) {
      try {
        const command = args.state === 'closed' ? 'close' : 'reopen';
        await execAsync(
          `gh issue ${command} ${args.issue_number} --repo ${args.repo}`
        );
```

## Exploitation Proof of Concept

When LLMs are tricked through prompt injection (and other techniques and attack vectors) to call the tool with input that uses special shell characters such as `; rm -rf /tmp;#` (be careful actually executing this payload) and other payload variations, the full command-line text will be interepted by the shell and result in other commands except of `ps` executing on the host running the MCP Server.

Reference example from prior security research on this topic, demonstrating how a similarly vulnerable MCP Server connected to Cursor is abused with prompt injection to bypass the developer's intended command:

![Cursor defined MCP Server vulnerable to command injection](https://res.cloudinary.com/snyk/image/upload/f_auto,w_2560,q_auto/v1747081395/Screenshot_2025-05-07_at_9.22.11_AM_d76kvm.png)

## Impact

User initiated and remote command injection on a running MCP Server.

## Recommendation

- Don't use `exec`. Use `execFile` instead, which pins the command and provides the arguments as array elements.
- If the user input is not a command-line flag, use the `--` notation to terminate command and command-line flag, and indicate that the text after the `--` double dash notation is benign value.

## References and Prior work

1. [Exploiting MCP Servers Vulnerable to Command Injection](https://snyk.io/articles/exploiting-mcp-servers-vulnerable-to-command-injection/)
2. Liran's [Node.js Secure Coding: Defending Against Command Injection Vulnerabilities](https://www.nodejs-security.com/book/command-injection)

## Credit

Disclosed by [Liran Tal](https://lirantal.com)

## References
- https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/security/advisories/GHSA-6jx8-rcjx-vmwf
- https://nvd.nist.gov/vuln/detail/CVE-2025-53818
- https://github.com/Sunwood-ai-labs/github-kanban-mcp-server
- https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/main/src/handlers/comment-handlers.ts#L8
- https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/main/src/handlers/tool-handlers.ts#L79
- https://github.com/Sunwood-ai-labs/github-kanban-mcp-server/blob/v0.4.0/src/handlers/comment-handlers.ts#L8-L23
