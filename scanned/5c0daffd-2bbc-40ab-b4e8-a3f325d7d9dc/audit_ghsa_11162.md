# [M] h3 has an observable timing discrepancy in basic auth utils

## Summary
Severity: Medium
Advisory: GHSA-26f5-8h2x-34xh
CVE: CVE-2026-33129
CWE: CWE-208
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-26f5-8h2x-34xh
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0-beta.0 <2.0.1-rc.9

## Details
### Summary
A Timing Side-Channel vulnerability exists in the `requireBasicAuth` function due to the use of unsafe string comparison (`!==`). This allows an attacker to deduce the valid password character-by-character by measuring the server's response time, effectively bypassing password complexity protections.

### Details
The vulnerability is located in the `requireBasicAuth` function. The code performs a standard string comparison between the user-provided password and the expected password:

~~~typescript
if (opts.password && password !== opts.password) {
  throw autheFailed(event, opts?.realm);
}
~~~

In V8 (and most runtime environments), the `!==` operator is optimized to "fail fast." It stops execution and returns `false` as soon as it encounters the first mismatched byte.
* If the first character is wrong, it returns immediately.
* If the first character is correct but the second is wrong, it takes slightly longer.

By statistically analyzing these minute timing differences over many requests, an attacker can determine the correct password one character at a time.

### PoC
This vulnerability is exploitable in real-world scenarios without direct access to the server machine.

To reproduce this, an attacker can send two packets (or bursts of packets) at the exact same time:
1.  **Packet A:** Contains a password that is known to be incorrect starting at the first character (e.g., `AAAA...`).
2.  **Packet B:** Contains a password where the first character is a guess (e.g., `B...`).

By measuring the time-to-first-byte (TTFB) or total response time of these concurrent requests, the attacker can filter out network jitter. If Packet B takes consistently longer to return than Packet A, the first character is confirmed as correct. This process is repeated for the second character, and so on. Tests confirm this timing difference is statistically consistent enough to recover credentials remotely.

### Impact

This vulnerability allows remote attackers to recover passwords. While network jitter makes this difficult over the internet, it is highly effective in local networks or cloud environments where the attacker is co-located. It reduces the complexity of cracking a password from exponential (guessing the whole string) to linear (guessing one char at a time).

## References
- https://github.com/h3js/h3/security/advisories/GHSA-26f5-8h2x-34xh
- https://nvd.nist.gov/vuln/detail/CVE-2026-33129
- https://github.com/h3js/h3/pull/1283
- https://github.com/h3js/h3
- https://github.com/h3js/h3/releases/tag/v2.0.1-rc.9
