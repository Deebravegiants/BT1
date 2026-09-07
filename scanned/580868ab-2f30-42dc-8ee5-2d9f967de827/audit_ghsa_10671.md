# [C] electerm: electerm_install_script_CommandInjection Vulnerability Report

## Summary
Severity: Critical
Advisory: GHSA-wxw2-rwmh-vr8f
CVE: CVE-2026-41500
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-wxw2-rwmh-vr8f
Type: github-advisory

## Affected
- npm: `electerm` — affected >=0 <3.3.8

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

**Command Injection vulnerabilities in electerm:**

A command injection vulnerability exists in `github.com/elcterm/electerm/npm/install.js:150`. The `runMac()` function appends attacker-controlled remote `releaseInfo.name` directly into an `exec("open ...")` command without validation.

**Who is impacted:** Users who run `npm install -g electerm` in Mac OS. An attacker who can control the remote release metadata (version string or release name) served by the project's update server could execute arbitrary system commands, tamper local files, and escalate compromise of development/runtime assets.

---

### Patches
_Has the problem been patched? What versions should users upgrade to?_

Fixed in [59708b38c8a52f5db59d7d4eff98e31d573128ee](https://github.com/electerm/electerm/commit/59708b38c8a52f5db59d7d4eff98e31d573128ee), user no need to upgrade, the new version already published in npm

---

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

no

---

### References
_Are there any links users can visit to find out more?_

[59708b38c8a52f5db59d7d4eff98e31d573128ee](https://github.com/electerm/electerm/commit/59708b38c8a52f5db59d7d4eff98e31d573128ee)

## References
- https://github.com/electerm/electerm/security/advisories/GHSA-wxw2-rwmh-vr8f
- https://nvd.nist.gov/vuln/detail/CVE-2026-41500
- https://github.com/electerm/electerm/commit/59708b38c8a52f5db59d7d4eff98e31d573128ee
- https://github.com/electerm/electerm
- https://github.com/electerm/electerm/releases/tag/v3.3.8
