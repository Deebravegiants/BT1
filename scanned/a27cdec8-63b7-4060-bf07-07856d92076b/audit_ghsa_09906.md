# [C] Axios npm Supply Chain Incident Impacting @usebruno/cli

## Summary
Severity: Critical
Advisory: GHSA-658g-p7jg-wx5g
CVE: CVE-2026-34841
CWE: CWE-1395, CWE-494, CWE-506
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-658g-p7jg-wx5g
Type: github-advisory

## Affected
- npm: `@usebruno/cli` — affected >=0 <3.2.1

## Details
### **Impact**

This is a **supply chain attack** involving compromised versions of the `axios` npm package, which introduced a hidden dependency deploying a cross-platform Remote Access Trojan (RAT).

Users of **@usebruno/cli** who ran `npm install` between **00:21 UTC and ~03:30 UTC on March 31, 2026** may have been impacted.

Potential impact includes:

* Execution of a malicious `postinstall` script
* Remote Access Trojan (RAT) installation
* Exfiltration of credentials and sensitive data

**Not impacted:**

* Bruno desktop app users
* Users who installed outside the attack window


### **Patches**

The compromised `axios` versions (`1.14.1`, `0.30.4`) have been **removed from npm**, and new installations will now resolve to safe versions.

Additionally, Bruno has taken further hardening steps:

* Pinned `axios` to a known safe version to prevent accidental resolution to malicious releases
* Fix implemented in: [https://github.com/usebruno/bruno/pull/7632](https://github.com/usebruno/bruno/pull/7632)


### **Recommendation**

If users installed **@usebruno/cli** during the affected window:
1. Reinstall dependencies
2. Rotate all credentials and secrets:

For additional guidance on securing your system, refer to this article:
https://www.aikido.dev/blog/axios-npm-compromised-maintainer-hijacked-rat

## References
- https://github.com/usebruno/bruno/security/advisories/GHSA-658g-p7jg-wx5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-34841
- https://github.com/axios/axios/issues/10604
- https://github.com/usebruno/bruno/pull/7632
- https://github.com/advisories/GHSA-fw8c-xr5c-95f9
- https://github.com/usebruno/bruno
- https://www.aikido.dev/blog/axios-npm-compromised-maintainer-hijacked-rat
