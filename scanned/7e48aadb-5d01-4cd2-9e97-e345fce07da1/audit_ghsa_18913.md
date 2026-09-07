# [M] js-yaml has prototype pollution in merge (<<)

## Summary
Severity: Medium
Advisory: GHSA-mh29-5h37-fv8m
CVE: CVE-2025-64718
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-mh29-5h37-fv8m
Type: github-advisory

## Affected
- npm: `js-yaml` — affected >=4.0.0 <4.1.1
- npm: `js-yaml` — affected >=0 <3.14.2

## Details
### Impact

In js-yaml 4.1.0, 4.0.0, and 3.14.1 and below, it's possible for an attacker to modify the prototype of the result of a parsed yaml document via prototype pollution (`__proto__`). All users who parse untrusted yaml documents may be impacted.

### Patches

Problem is patched in js-yaml 4.1.1 and 3.14.2.

### Workarounds

You can protect against this kind of attack on the server by using `node --disable-proto=delete` or `deno` (in Deno, pollution protection is on by default).

### References

https://cheatsheetseries.owasp.org/cheatsheets/Prototype_Pollution_Prevention_Cheat_Sheet.html

## References
- https://github.com/nodeca/js-yaml/security/advisories/GHSA-mh29-5h37-fv8m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64718
- https://github.com/nodeca/js-yaml/issues/730#issuecomment-3549635876
- https://github.com/nodeca/js-yaml/commit/383665ff4248ec2192d1274e934462bb30426879
- https://github.com/nodeca/js-yaml/commit/5278870a17454fe8621dbd8c445c412529525266
- https://github.com/advisories/GHSA-mh29-5h37-fv8m
- https://github.com/nodeca/js-yaml
