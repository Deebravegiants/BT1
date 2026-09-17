# [H] convict vulnerable to Prototype Pollution

## Summary
Severity: High
Advisory: GHSA-4jrm-c32x-w4jf
CVE: CVE-2023-0163
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-10
Source: https://github.com/advisories/GHSA-4jrm-c32x-w4jf
Type: github-advisory

## Affected
- npm: `convict` — affected >=0 <6.2.4

## Details
### Impact

* An attacker can inject attributes that are used in other components
* An attacker can override existing attributes with ones that have incompatible type, which may lead to a crash.

The main use case of Convict is for handling server-side configurations written by the admins owning the servers, and not random users. So it's unlikely that an admin would deliberately sabotage their own server. Still a situation can happen where an admin not knowledgeable about JavaScript could be tricked by an attacker into writing the malicious JavaScript code into some config files.

### Patches
The problem is patched in `convict@6.2.4`. Users should upgrade to `convict@6.2.4`.

### Workarounds
No way for users to fix or remediate the vulnerability without upgrading

### References
https://github.com/mozilla/node-convict/issues/410

## References
- https://github.com/mozilla/node-convict/security/advisories/GHSA-4jrm-c32x-w4jf
- https://nvd.nist.gov/vuln/detail/CVE-2023-0163
- https://github.com/mozilla/node-convict/issues/410
- https://github.com/mozilla/node-convict/commit/fb602fbe1e9f14f2e88ecb8179d0f76466d21ecb
- https://github.com/mozilla/node-convict
