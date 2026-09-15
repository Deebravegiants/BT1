# [C] Unsafe fall-through in getWhereConditions

## Summary
Severity: Critical
Advisory: GHSA-vqfx-gj96-3w95
CVE: CVE-2023-22579
CWE: CWE-843
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-23
Source: https://github.com/advisories/GHSA-vqfx-gj96-3w95
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <6.28.1
- npm: `@sequelize/core` — affected >=0 <7.0.0-alpha.20

## Details
### Impact

Providing an invalid value to the `where` option of a query caused Sequelize to ignore that option instead of throwing an error. 

A finder call like the following did not throw an error:

```ts
User.findAll({
  where: new Date(),
});
```

As this option is typically used with plain javascript objects, be aware that this only happens at the top level of this option.

### Patches

This issue has been patched in [`sequelize@6.28.1`](https://github.com/sequelize/sequelize/pull/15699) & [`@sequelize/core@7.0.0.alpha-20`](https://github.com/sequelize/sequelize/pull/15375)

### References

A discussion thread about this issue is open at https://github.com/sequelize/sequelize/discussions/15698

CVE:  CVE-2023-22579
Snyk: https://security.snyk.io/vuln/SNYK-JS-SEQUELIZE-3324090

## References
- https://github.com/sequelize/sequelize/security/advisories/GHSA-vqfx-gj96-3w95
- https://nvd.nist.gov/vuln/detail/CVE-2023-22579
- https://github.com/sequelize/sequelize/pull/15375
- https://github.com/sequelize/sequelize/pull/15699
- https://csirt.divd.nl/CVE-2023-22579
- https://csirt.divd.nl/DIVD-2022-00020
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/discussions/15698
- https://github.com/sequelize/sequelize/releases/tag/v6.28.1
- https://github.com/sequelize/sequelize/releases/tag/v7.0.0-alpha.20
