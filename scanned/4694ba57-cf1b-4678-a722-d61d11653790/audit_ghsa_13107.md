# [H] Trigger `beforeFind` not invoked in internal query pipeline when fetching pointer

## Summary
Severity: High
Advisory: GHSA-fcv6-fg5r-jm9q
CVE: CVE-2023-41058
CWE: CWE-670
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-04
Source: https://github.com/advisories/GHSA-fcv6-fg5r-jm9q
Type: github-advisory

## Affected
- npm: `parse-server` — affected >=1.0.0 <5.5.5
- npm: `parse-server` — affected >=6.0.0 <6.2.2

## Details
### Impact

A Parse Pointer can be used to access internal Parse Server classes. It can also be used to circumvent the `beforeFind` query trigger which can be an additional vulnerability for deployments where the `beforeFind` trigger is used as a security layer to modify an incoming query.

### Patches

The vulnerability was fixed by implementing a patch in the internal query pipeline to prevent a Parse Pointer to be used to access internal Parse Server classes or circumvent the `beforeFind` trigger.

### Workarounds

There is no known workaround to prevent a Parse Pointer to be used to access internal Parse Server classes. A workaround if a `beforeFind` trigger is used as a security layer is to instead use the Parse Server provided [security layers](https://docs.parseplatform.org/parse-server/guide/#security) to manage access levels with Class-Level Permissions and Object-Level Access Control.

### References

- GitHub security advisory: https://github.com/parse-community/parse-server/security/advisories/GHSA-fcv6-fg5r-jm9q
- Patched in Parse Server 6.x: https://github.com/parse-community/parse-server/releases/tag/6.2.2
- Patched in Parse Server 5.x (LTS): https://github.com/parse-community/parse-server/releases/tag/5.5.5

## References
- https://github.com/parse-community/parse-server/security/advisories/GHSA-fcv6-fg5r-jm9q
- https://nvd.nist.gov/vuln/detail/CVE-2023-41058
- https://github.com/parse-community/parse-server/commit/be4c7e23c63a2fb690685665cebed0de26be05c5
- https://docs.parseplatform.org/parse-server/guide/#security
- https://github.com/parse-community/parse-server
- https://github.com/parse-community/parse-server/releases/tag/5.5.5
- https://github.com/parse-community/parse-server/releases/tag/6.2.2
