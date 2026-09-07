# [C] zeptoclaw has Shell allowlist-blocklist bypass via command/argument injection and file name wildcards

## Summary
Severity: Critical
Advisory: GHSA-5wp8-q9mx-8jx8
CWE: CWE-77
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-5wp8-q9mx-8jx8
Type: github-advisory

## Affected
- crates.io: `zeptoclaw` — affected >=0 <0.6.2

## Details
### Summary
[zeptoclaw](https://github.com/qhkm/zeptoclaw) implements a allowlist combined with a blocklist to prevent malicious shell commands in [src/security/shell.rs](https://github.com/qhkm/zeptoclaw/blob/v0.5.8/src/security/shell.rs). However, even in the `Strict` mode, attackers can completely bypass all the guards from allowlist and blocklist:

- to bypass the `allowlist`, command injection is enough, such as `;`, `$()` etc.
- to bypass the `REGEX_BLOCKED_PATTERNS`, argument injection is enough, such as the `python3 -P -c "..."`
- to bypass the `LITERAL_BLOCKED_PATTERNS`, file name wildcards can do the work, such as `cat /etc/pass[w]d`

### Details
In code [src/security/shell.rs#L218-L243](https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/security/shell.rs#L218-L243), one can see the allowlist only checks the first token and thus makes command injection possible. 
```rust
        // Allowlist check (runs after blocklist)
        if self.allowlist_mode != ShellAllowlistMode::Off && !self.allowlist.is_empty() {
            let first_token = command
                .split_whitespace()
                .next()
                .unwrap_or("")
                .to_lowercase();
            // Strip path prefix (e.g. /usr/bin/git -> git)
            let executable = first_token.rsplit('/').next().unwrap_or(&first_token);
            if !self.allowlist.iter().any(|a| a == executable) {
                match self.allowlist_mode {
                    ShellAllowlistMode::Strict => {
                        return Err(ZeptoError::SecurityViolation(format!(
                            "Command '{}' not in allowlist",
                            executable
                        )));
                    }
                    ShellAllowlistMode::Warn => {
                        tracing::warn!(
                            command = %command,
                            executable = %executable,
                            "Command not in allowlist"
                        );
                    }
                    ShellAllowlistMode::Off => {} // unreachable
                }
```
 `!self.allowlist.is_empty()` makes the empty allowlist overlook the allowlist check, if it is in `ShellAllowlistMode::Strict` mode, empty allowlist should direct reject all the commands.

As the code in [src/security/shell.rs#L18-L70](https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/security/shell.rs#L18-L70), we can find the `REGEX_BLOCKED_PATTERNS` only apply `\s+` in between the command and arguments, making argument injection possible, and the `LITERAL_BLOCKED_PATTERNS` just uses specific file name, totally overlooking the file name wildcards:
```rust
const REGEX_BLOCKED_PATTERNS: &[&str] = &[
    // Piped shell execution (curl/wget to sh/bash)
    r"curl\s+.*\|\s*(sh|bash|zsh)",
    r"wget\s+.*\|\s*(sh|bash|zsh)",
    r"\|\s*(sh|bash|zsh)\s*$",
    // Reverse shells
    r"bash\s+-i\s+>&\s*/dev/tcp",
    r"nc\s+.*-e\s+(sh|bash|/bin)",
    r"/dev/tcp/",
    r"/dev/udp/",
    // Destructive root operations (various flag orderings)
    r"rm\s+(-[rf]{1,2}\s+)*(-[rf]{1,2}\s+)*/\s*($|;|\||&)",
    r"rm\s+(-[rf]{1,2}\s+)*(-[rf]{1,2}\s+)*/\*\s*($|;|\||&)",
    // Format/overwrite disk
    r"mkfs(\.[a-z0-9]+)?\s",
    r"dd\s+.*if=/dev/(zero|random|urandom).*of=/dev/[sh]d",
    r">\s*/dev/[sh]d[a-z]",
    // System-wide permission changes
    r"chmod\s+(-R\s+)?777\s+/\s*$",
    r"chmod\s+(-R\s+)?777\s+/[a-z]",
    // Fork bombs
    r":\(\)\s*\{\s*:\|:&\s*\}\s*;:",
    r"fork\s*\(\s*\)",
    // Encoded/indirect execution (common blocklist bypasses)
    r"base64\s+(-d|--decode)",
    r"python[23]?\s+-c\s+",
    r"perl\s+-e\s+",
    r"ruby\s+-e\s+",
    r"node\s+-e\s+",
    r"\beval\s+",
    r"xargs\s+.*sh\b",
    r"xargs\s+.*bash\b",
    // Environment variable exfiltration
    r"\benv\b.*>\s*/",
    r"\bprintenv\b.*>\s*/",
];

/// Literal substring patterns (credentials, sensitive paths)
const LITERAL_BLOCKED_PATTERNS: &[&str] = &[
    "/etc/shadow",
    "/etc/passwd",
    "~/.ssh/",
    ".ssh/id_rsa",
    ".ssh/id_ed25519",
    ".ssh/id_ecdsa",
    ".ssh/id_dsa",
    ".ssh/authorized_keys",
    ".aws/credentials",
    ".kube/config",
    // ZeptoClaw's own config (contains API keys and channel tokens)
    ".zeptoclaw/config.json",
    ".zeptoclaw/config.yaml",
];
```

### PoC
```rust
    #[test]
    fn test_allowlist_bypass() {
        let config =
            ShellSecurityConfig::new().with_allowlist(vec!["git"], ShellAllowlistMode::Strict);
        assert!(config.validate_command("/usr/bin/git status; python -P -c 'import os; os.system(\"rm -rf /\")'; cat /etc/pass[w]d").is_ok());
    }
```

### Impact
Unauthorized command execution.

### Credit
[@zpbrent](https://github.com/zpbrent)

## References
- https://github.com/qhkm/zeptoclaw/security/advisories/GHSA-5wp8-q9mx-8jx8
- https://github.com/qhkm/zeptoclaw/commit/68916c3e4f3af107f11940b27854fc7ef517058b
- https://github.com/qhkm/zeptoclaw
- https://github.com/qhkm/zeptoclaw/blob/fe2ef07cfec5bb46b42cdd65f52b9230c03e9270/src/security/shell.rs#L218-L243
