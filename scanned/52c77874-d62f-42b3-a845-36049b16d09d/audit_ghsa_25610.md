# [H] Prototype Pollution in convict

## Summary
Severity: High
Advisory: GHSA-x2w5-725j-gf2g
CVE: CVE-2022-22143
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-20
Source: https://github.com/advisories/GHSA-x2w5-725j-gf2g
Type: github-advisory

## Affected
- npm: `convict` — affected >=0 <6.2.3

## Details
### Impact

* An attacker can inject attributes that are used in other components
* An attacker can override existing attributes with ones that have incompatible type, which may lead to a crash.

The main use case of Convict is for handling server-side configurations written by the admins owning the servers, and not random users. So it's unlikely that an admin would deliberately sabotage their own server. Still a situation can happen where an admin not knowledgeable about JavaScript could be tricked by an attacker into writing the malicious JavaScript code into some config files.

### Patches

The problem is patched in `convict@6.2.3`. Users should upgrade to `convict@6.2.3`.

### Workarounds

No way for users to fix or remediate the vulnerability without upgrading

### References

* https://www.huntr.dev/bounties/1-npm-convict/
* #384
* 3b86be087d8f14681a9c889d45da7fe3ad9cd880
* 1ea0ab19c5208f66509e1c43b0d0f21c1fd29b75

### For more information

If you have any questions or comments about this advisory: 
add your question as a comment in #384

## References
- https://github.com/mozilla/node-convict/security/advisories/GHSA-x2w5-725j-gf2g
- https://nvd.nist.gov/vuln/detail/CVE-2022-22143
- https://github.com/mozilla/node-convict/pull/384
- https://github.com/mozilla/node-convict/commit/3b86be087d8f14681a9c889d45da7fe3ad9cd880
- https://github.com/mozilla/node-convict
- https://github.com/mozilla/node-convict/blob/5eb1314f85346760a3c31cb14510f2f0af11d0d3/packages/convict/src/main.js%23L569
- https://github.com/mozilla/node-convict/releases/tag/v6.2.2
- https://snyk.io/vuln/SNYK-JS-CONVICT-2340604
- https://www.huntr.dev/bounties/1-npm-convict
