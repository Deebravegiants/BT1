# [C] Cryptographically weak PRNG in `utils.generateUUID`

## Summary
Severity: Critical
Advisory: GHSA-p4cc-w597-6cpm
CVE: CVE-2022-36045
CWE: CWE-330, CWE-338
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-30
Source: https://github.com/advisories/GHSA-p4cc-w597-6cpm
Type: github-advisory

## Affected
- npm: `nodebb` — affected >=0 <1.19.8
- npm: `nodebb` — affected >=2.0.0 <2.0.1

## Details
### In Brief
`utils.generateUUID`, a helper function available in essentially all versions of NodeBB (as far back as v1.0.1 and potentially earlier) used a cryptographically insecure Pseudo-random number generator (`Math.random()`), which meant that a specially crafted script combined with multiple invocations of the password reset functionality could enable an attacker to correctly calculate the reset code for an account they do not have access to.

### Impact
This vulnerability impacts all installations of NodeBB. The vulnerability allows for an attacker to take over any account without the involvement of the victim, and as such, the remediation should be applied immediately (either via NodeBB upgrade or cherry-pick of the specific changeset. Patches have been provided for both active branches of NodeBB (v2.x and v1.19.x)—please see below.

If you are already on v2.0.0 or v1.19.7, you can upgrade with no ill effects. The new version contains only the patch for this vulnerability.

The impact of this vulnerability is slightly lessened by the requirement that the target's email address must be known, **and** user emails are protected values in NodeBB. However, since NodeBB can be configured to display email addresses if the admin so wishes, and as email addresses can often by derived from other sources and/or guessed, the impact of this vulnerability is still fairly high.

### Patches

#### v2.x
The vulnerability has been patched in https://github.com/NodeBB/NodeBB/commit/e802fab87f94a13f397f04cfe6068f2f7ddf7888. You can cherry-pick this directly into your codebase.

#### v1.19.x
The vulnerability has been patched in 81e3c1ba488d03371a5ce8d0ebb5c5803026e0f9. You can cherry-pick this directly into your codebase.

### Workarounds
There is no known workaround, but the patch sets listed above will fully patch the vulnerability.

### References
* [CWE-338: Use of Cryptographically Weak Pseudo-Random Number Generator (PRNG)](http://cwe.mitre.org/data/definitions/338.html)

### For more information
If you have any questions or comments about this advisory:
* Discuss it on [our community forum](community.nodebb.org/)
* Email us at [support@nodebb.org](mailto:support@nodebb.org)

## References
- https://github.com/NodeBB/NodeBB/security/advisories/GHSA-p4cc-w597-6cpm
- https://nvd.nist.gov/vuln/detail/CVE-2022-36045
- https://github.com/NodeBB/NodeBB/commit/81e3c1ba488d03371a5ce8d0ebb5c5803026e0f9
- https://github.com/NodeBB/NodeBB/commit/e802fab87f94a13f397f04cfe6068f2f7ddf7888
- https://github.com/NodeBB/NodeBB
