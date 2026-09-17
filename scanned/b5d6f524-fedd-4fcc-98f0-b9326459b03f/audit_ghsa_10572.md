# [M] Axios has a NO_PROXY Hostname Normalization Bypass that Leads to SSRF

## Summary
Severity: Medium
Advisory: GHSA-3p68-rc4w-qgx5
CVE: CVE-2025-62718
CWE: CWE-441, CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-3p68-rc4w-qgx5
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.0.0 <1.15.0
- npm: `axios` — affected >=0 <0.31.0

## Details
Axios does not correctly handle hostname normalization when checking `NO_PROXY` rules.
Requests to loopback addresses like `localhost.` (with a trailing dot) or `[::1]` (IPv6 literal) skip `NO_PROXY` matching and go through the configured proxy.

This goes against what developers expect and lets attackers force requests through a proxy, even if `NO_PROXY` is set up to protect loopback or internal services.

According to [RFC 1034 §3.1](https://datatracker.ietf.org/doc/html/rfc1034#section-3.1) and [RFC 3986 §3.2.2](https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.2), a hostname can have a trailing dot to show it is a fully qualified domain name (FQDN). At the DNS level, `localhost.` is the same as `localhost`. 
However, Axios does a literal string comparison instead of normalizing hostnames before checking `NO_PROXY`. This causes requests like `http://localhost.:8080/` and `http://[::1]:8080/` to be incorrectly proxied.

This issue leads to the possibility of proxy bypass and SSRF vulnerabilities allowing attackers to reach sensitive loopback or internal services despite the configured protections.

---

**PoC**

```js
import http from "http";
import axios from "axios";

const proxyPort = 5300;

http.createServer((req, res) => {
  console.log("[PROXY] Got:", req.method, req.url, "Host:", req.headers.host);
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("proxied");
}).listen(proxyPort, () => console.log("Proxy", proxyPort));

process.env.HTTP_PROXY = `http://127.0.0.1:${proxyPort}`;
process.env.NO_PROXY = "localhost,127.0.0.1,::1";

async function test(url) {
  try {
    await axios.get(url, { timeout: 2000 });
  } catch {}
}

setTimeout(async () => {
  console.log("\n[*] Testing http://localhost.:8080/");
  await test("http://localhost.:8080/"); // goes through proxy

  console.log("\n[*] Testing http://[::1]:8080/");
  await test("http://[::1]:8080/"); // goes through proxy
}, 500);
```

**Expected:** Requests bypass the proxy (direct to loopback).
**Actual:** Proxy logs requests for `localhost.` and `[::1]`.

---

**Impact**

* Applications that rely on `NO_PROXY=localhost,127.0.0.1,::1` for protecting loopback/internal access are vulnerable.
* Attackers controlling request URLs can:

  * Force Axios to send local traffic through an attacker-controlled proxy.
  * Bypass SSRF mitigations relying on NO\_PROXY rules.
  * Potentially exfiltrate sensitive responses from internal services via the proxy.
  
  
---

**Affected Versions**

* Confirmed on Axios **1.12.2** (latest at time of testing).
* affects all versions that rely on Axios’ current `NO_PROXY` evaluation.

---

**Remediation**
Axios should normalize hostnames before evaluating `NO_PROXY`, including:

* Strip trailing dots from hostnames (per RFC 3986).
* Normalize IPv6 literals by removing brackets for matching.

## References
- https://github.com/axios/axios/security/advisories/GHSA-3p68-rc4w-qgx5
- https://nvd.nist.gov/vuln/detail/CVE-2025-62718
- https://github.com/axios/axios/pull/10661
- https://github.com/axios/axios/pull/10688
- https://github.com/axios/axios/commit/03cdfc99e8db32a390e12128208b6778492cee9c
- https://github.com/axios/axios/commit/fb3befb6daac6cad26b2e54094d0f2d9e47f24df
- https://datatracker.ietf.org/doc/html/rfc1034#section-3.1
- https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.2
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v0.31.0
- https://github.com/axios/axios/releases/tag/v1.15.0
