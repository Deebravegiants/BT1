# [M] @simonsmith/cypress-image-snapshothas fix for insecure snapshot file names

## Summary
Severity: Medium
Advisory: GHSA-vxjg-hchx-cc4g
CVE: CVE-2023-38695
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-vxjg-hchx-cc4g
Type: github-advisory

## Affected
- npm: `@simonsmith/cypress-image-snapshot` — affected >=0 <8.0.2

## Details
### Impact
It's possible for a user to pass a relative file path for the snapshot name and reach outside of the project directory into the machine running the test. Example:

```js
  cy.get('h1').matchImageSnapshot('../../../ignore-relative-dirs')
```
The above will create an `ignore-relative-dirs.png` three levels up

### Patches
Fixed in `8.0.2`

### Workarounds
Validate all the existing uses of `matchImageSnapshot` to ensure correct use of the filename argument. Example:

```js
    // snapshot name will be the test title
    cy.matchImageSnapshot();

    // snapshot name will be the name passed in
    cy.matchImageSnapshot('login');
```

### References
https://github.com/simonsmith/cypress-image-snapshot/issues/15

## References
- https://github.com/simonsmith/cypress-image-snapshot/security/advisories/GHSA-vxjg-hchx-cc4g
- https://nvd.nist.gov/vuln/detail/CVE-2023-38695
- https://github.com/simonsmith/cypress-image-snapshot/issues/15
- https://github.com/simonsmith/cypress-image-snapshot/commit/ef49519795daf5183f4fac6f3136e194f20f39f4
- https://github.com/simonsmith/cypress-image-snapshot
- https://github.com/simonsmith/cypress-image-snapshot/releases/tag/8.0.2
