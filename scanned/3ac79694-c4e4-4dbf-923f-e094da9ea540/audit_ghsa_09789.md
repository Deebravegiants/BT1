# [M] Axios HTTP/2 Session Cleanup State Corruption Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qj83-cq47-w5f8
CVE: CVE-2026-39865
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-qj83-cq47-w5f8
Type: github-advisory

## Affected
- npm: `axios` — affected >=1.13.0 <1.13.2

## Details
### Summary

Axios HTTP/2 session cleanup logic contains a state corruption bug that allows a malicious server to crash the client process through concurrent session closures. This denial-of-service vulnerability affects axios versions prior to 1.13.2 when HTTP/2 is enabled.

### Details

The vulnerability exists in the `Http2Sessions.getSession()` method in `lib/adapters/http.js`. The session cleanup logic contains a control flow error when removing sessions from the sessions array.

**Vulnerable Code:**
```javascript
while (i--) {
  if (entries[i][0] === session) {
    entries.splice(i, 1);
    if (len === 1) {
      delete this.sessions[authority];
      return;
    }
  }
}
```

**Root Cause:**
After calling `entries.splice(i, 1)` to remove a session, the original code only returned early if `len === 1`. For arrays with multiple entries, the iteration continued after modifying the array, causing undefined behavior and potential crashes when accessing shifted array indices.

**Fixed Code:**
```javascript
while (i--) {
  if (entries[i][0] === session) {
    if (len === 1) {
      delete this.sessions[authority];
    } else {
      entries.splice(i, 1);
    }
    return;
  }
}
```

The fix restructures the control flow to immediately return after removing a session, regardless of whether the array is being emptied or just having one element removed. This prevents continued iteration over a modified array and eliminates the state corruption vulnerability.

**Affected Component:**
- `lib/adapters/http.js` - Http2Sessions class, session cleanup in connection close handler

### PoC

1. Set up a malicious HTTP/2 server that accepts multiple concurrent connections from an axios client
2. Establish multiple concurrent HTTP/2 sessions with the axios client
3. Close all sessions simultaneously with precise timing
4. The flawed cleanup logic attempts to iterate over and modify the sessions array concurrently
5. This causes the client to access invalid memory locations, resulting in a process crash

**Prerequisites:**
- Client must use axios with HTTP/2 enabled
- Client must connect to attacker-controlled HTTP/2 server
- Multiple concurrent HTTP/2 sessions must be established
- Server must close all sessions simultaneously with precise timing

### Impact

**Who is impacted:**
- Applications using axios with HTTP/2 enabled
- Applications connecting to untrusted or attacker-controlled HTTP/2 servers
- Node.js applications using axios for HTTP/2 requests

**Impact Details:**
- **Denial of Service:** Malicious server can crash the axios client process by accepting and closing multiple concurrent HTTP/2 connections simultaneously
- **Availability Impact:** Complete loss of availability for the client process through crash (though service may auto-restart)
- **Scope:** Impact is limited to the single client process making the requests; does not escape to affect other components or systems
- **No Confidentiality or Integrity Impact:** Vulnerability only causes process crash, no information disclosure or data modification

**CVSS Score:** 5.9 (Medium)
**CVSS Vector:** CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H

**CWE Classifications:**
- CWE-400: Uncontrolled Resource Consumption
- CWE-662: Improper Synchronization

## References
- https://github.com/axios/axios/security/advisories/GHSA-qj83-cq47-w5f8
- https://nvd.nist.gov/vuln/detail/CVE-2026-39865
- https://github.com/axios/axios/commit/0588880ac7ddba7594ef179930493884b7e90bf5
- https://github.com/axios/axios
- https://github.com/axios/axios/releases/tag/v1.13.2
