# [M] Zen-C Vulnerable to Command Injection via Malicious Output Filename

## Summary
Severity: Medium
Advisory: CVE-2026-28207
Aliases: GHSA-9rff-x96h-76h2
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L)
Published: 2026-02-26
Source: https://osv.dev/vulnerability/CVE-2026-28207
Type: osv

## Details
Zen C is a systems programming language that compiles to human-readable GNU C/C11. Prior to version 0.4.2, a command injection vulnerability (CWE-78) in the Zen C compiler allows local attackers to execute arbitrary shell commands by providing a specially crafted output filename via the `-o` command-line argument. The vulnerability existed in the `main` application logic (specifically in `src/main.c`), where the compiler constructed a shell command string to invoke the backend C compiler. This command string was built by concatenating various arguments, including the user-controlled output filename, and was subsequently executed using the `system()` function. Because `system()` invokes a shell to parse and execute the command, shell metacharacters within the output filename were interpreted by the shell, leading to arbitrary command execution. An attacker who can influence the command-line arguments passed to the `zc` compiler (like through a build script or a CI/CD pipeline configuration) can execute arbitrary commands with the privileges of the user running the compiler. The vulnerability has been fixed in version 0.4.2 by removing `system()` calls, implementing `ArgList`, and internal argument handling. Users are advised to update to Zen C version v0.4.2 or later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28207.json
- https://github.com/z-libs/Zen-C/security/advisories/GHSA-9rff-x96h-76h2
- https://nvd.nist.gov/vuln/detail/CVE-2026-28207
- https://f0nduesav0yarde.github.io/blog/vulnerabilities/cve-2026-28207/
