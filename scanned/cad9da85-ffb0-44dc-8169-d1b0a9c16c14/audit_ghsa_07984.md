# [H] godot-mcp has Command Injection via unsanitized projectPath

## Summary
Severity: High
Advisory: GHSA-8jx2-rhfh-q928
CVE: CVE-2026-25546
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-8jx2-rhfh-q928
Type: github-advisory

## Affected
- npm: `@coding-solo/godot-mcp` — affected >=0 <0.1.1

## Details
### Impact 
A Command Injection vulnerability in godot-mcp allows remote code execution. The `executeOperation` function passed user-controlled input (e.g., `projectPath`) directly to `exec()`, which spawns a shell. An attacker could inject shell metacharacters like `$(command)` or `&calc` to execute arbitrary commands with the privileges of the MCP server process. 

This affects any tool that accepts `projectPath`, including `create_scene`, `add_node`, `load_sprite`, and others. 

### Patches 
Fixed in version 0.1.1 by switching from `exec()` to `execFile()`, which does not invoke a shell. 

### Workarounds 
None. Users should upgrade immediately. 

### Resources
 - https://github.com/Coding-Solo/godot-mcp/issues/64
 - https://github.com/Coding-Solo/godot-mcp/pull/67

## References
- https://github.com/Coding-Solo/godot-mcp/security/advisories/GHSA-8jx2-rhfh-q928
- https://nvd.nist.gov/vuln/detail/CVE-2026-25546
- https://github.com/Coding-Solo/godot-mcp/issues/64
- https://github.com/Coding-Solo/godot-mcp/pull/67
- https://github.com/Coding-Solo/godot-mcp/commit/21c785d923cfdb471ea60323c13807d62dfecc5a
- https://github.com/Coding-Solo/godot-mcp
