# [H] Systeminformation has a Command Injection via unsanitized interface parameter in wifi.js retry path

## Summary
Severity: High
Advisory: GHSA-9c88-49p5-5ggf
CVE: CVE-2026-26280
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-18
Source: https://github.com/advisories/GHSA-9c88-49p5-5ggf
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <5.30.8

## Details
### Summary
A command injection vulnerability in the `wifiNetworks()` function allows an attacker to execute arbitrary OS commands via an unsanitized network interface parameter in the retry code path.

### Details
In `lib/wifi.js`, the `wifiNetworks()` function sanitizes the `iface` parameter on the initial call (line 437). However, when the initial scan returns empty results, a `setTimeout` retry (lines 440-441) calls `getWifiNetworkListIw(iface)` with the **original unsanitized** `iface` value, which is passed directly to `execSync('iwlist ${iface} scan')`.

### PoC
1. Install `systeminformation@5.30.7`
2. Call `si.wifiNetworks('eth0; id')`
3. The first call sanitizes input, but if results are empty, the retry executes: `iwlist eth0; id scan`

### Impact
Remote Code Execution (RCE). Any application passing user-controlled input to `si.wifiNetworks()` is vulnerable to arbitrary command execution with the privileges of the Node.js process.

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-9c88-49p5-5ggf
- https://nvd.nist.gov/vuln/detail/CVE-2026-26280
- https://github.com/sebhildebrandt/systeminformation/commit/22242aa56188f2bffcbd7d265a11e1ebb808b460
- https://github.com/sebhildebrandt/systeminformation
