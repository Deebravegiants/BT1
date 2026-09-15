# [M] Pkg Local Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-22r3-9w55-cj54
CVE: CVE-2024-24828
CWE: CWE-276
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-22r3-9w55-cj54
Type: github-advisory

## Affected
- npm: `pkg` — affected >=0

## Details
### Impact
Any native code packages built by `pkg` are written to a hardcoded directory. On unix systems, this is `/tmp/pkg/*` which is a shared directory for all users on the same local system. There is no uniqueness to the package names within this directory, they are predictable.

An attacker who has access to the same local system has the ability to replace the genuine executables in the shared directory with malicious executables of the same name. A user may then run the malicious executable without realising it has been modified.

### Patches
This package is deprecated. Therefore, there will not be a patch provided for this vulnerability.

### Recommended Action:
To check if your executable build by pkg depends on native code and is vulnerable, run the executable and check if `/tmp/pkg/` was created.

Users should transition to actively maintained alternatives. We would recommend investigating Node.js 21’s support for [single executable applications](https://nodejs.org/api/single-executable-applications.html).

### Workarounds
Given the decision to deprecate the pkg package, there are no official workarounds or remediations provided by our team. Users should prioritize migrating to other packages that offer similar functionality with enhanced security.

## References
- https://github.com/vercel/pkg/security/advisories/GHSA-22r3-9w55-cj54
- https://nvd.nist.gov/vuln/detail/CVE-2024-24828
- https://github.com/vercel/pkg
- https://nodejs.org/api/single-executable-applications.html
