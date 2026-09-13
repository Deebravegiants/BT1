# [C] electerm has Command Injection via runLinux funtion

## Summary
Severity: Critical
Advisory: GHSA-8x35-hph8-37hq
CVE: CVE-2026-41501
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-8x35-hph8-37hq
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.3.8

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

**Command Injection vulnerabilities in electerm:**

A command injection vulnerability exists in `github.com/elcterm/electerm/npm/install.js:130`. The `runLinux()` function appends attacker-controlled remote version strings directly into an `exec("rm -rf ...")` command without validation.

**Who is impacted:** Users who run `npm install -g electerm` in Linux. An attacker who can control the remote release metadata (version string or release name) served by the project's update server could execute arbitrary system commands, tamper local files, and escalate compromise of development/runtime assets.

---

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Fixed in [59708b38c8a52f5db59d7d4eff98e31d573128ee](https://github.com/electerm/electerm/commit/59708b38c8a52f5db59d7d4eff98e31d573128ee), user no need to upgrade, the new version already published in npm

---

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

no

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-8x35-hph8-37hq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41501
- https://github.com/electerm/electerm/commit/59708b38c8a52f5db59d7d4eff98e31d573128ee
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.3.8
