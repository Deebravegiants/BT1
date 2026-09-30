# [H] node-opcua: Unbounded nonce cache enables unauthenticated heap exhaustion DoS

## Summary
Severity: High
Advisory: GHSA-6wvw-vrw4-363w
CVE: CVE-2026-54156
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-6wvw-vrw4-363w
Type: github-advisory

## Affected
- npm: `node-opcua` — affected >=0 <2.166.0

## Details
**Summary**
A process-global nonce cache with no eviction policy allows an unauthenticated remote attacker to exhaust server heap memory by repeatedly opening sessions, causing the node-opcua server process to crash.

**Affected versions:** <= 2.165.0
**Tested version:** 2.165.0
**CVSS Score:** 7.5 (High)
**CVSS Vector:** CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H
**CWE:** CWE-770 Allocation of Resources Without Limits or Throttling

---

**Root Cause**

In `packages/node-opcua-secure-channel/source/server/server_secure_channel_layer.ts` at line 156, `g_alreadyUsedNonce` is a process-global object used to track previously seen nonces for replay detection. Entries are added on every `OpenSecureChannelRequest` and every `CreateSession` request but are never removed or expired.

An unauthenticated attacker can exploit the `CreateSession` path (which requires no certificate) to accumulate nonce entries indefinitely. Even with `maxSessions=10` limiting concurrent sessions, nonces persist after session expiry, allowing slow but reliable heap exhaustion across repeated connection cycles.

---

**Measured Impact**

Dynamically confirmed heap growth:
- 5,000 unique nonces → +1.23 MB resident heap, no eviction after explicit GC
- Projected: 10^6 nonces → ~246 MB resident heap
- Achievable OOM on default Node.js heap limits

---

**Suggested Fix**

Add a TTL-based eviction policy to `g_alreadyUsedNonce`. Nonces should be expired after the maximum session timeout (or a reasonable fixed window, e.g. 1 hour). A Map with timestamp entries and periodic cleanup is sufficient.

---

I am following a 90-day responsible disclosure policy. I am happy to provide additional technical details under embargo. Please confirm receipt at your earliest convenience.

Reporter: Stanley Tobias
Discovery date: 2026-03-23

## References
- https://github.com/node-opcua/node-opcua/security/advisories/GHSA-6wvw-vrw4-363w
- https://github.com/node-opcua/node-opcua/commit/b82c2939fe9c658de58da993f2798ec5481d7313
- https://github.com/node-opcua/node-opcua
- https://github.com/node-opcua/node-opcua/releases/tag/v2.166.0
