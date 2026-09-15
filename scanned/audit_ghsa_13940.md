# [C] Sequelize - Default support for “raw attributes” when using parentheses

## Summary
Severity: Critical
Advisory: GHSA-f598-mfpv-gmfx
CVE: CVE-2023-22578
CWE: CWE-790
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-24
Source: https://github.com/advisories/GHSA-f598-mfpv-gmfx
Type: github-advisory

## Affected
- npm: `@sequelize/core` — affected >=0 <7.0.0-alpha.20
- npm: `sequelize` — affected >=0 <6.29.0

## Details
### Impact

Sequelize 6.28.2 and prior has a dangerous feature where using parentheses in the attribute option would make Sequelize use the string as-is in the SQL

```ts
User.findAll({
  attributes: [
    ['count(id)', 'count']
  ]
});
```

Produced

```sql
SELECT count(id) AS "count" FROM "users"
```

### Patches

This feature was deprecated in Sequelize 5, and using it prints a deprecation warning.

This issue has been patched in [`@sequelize/core@7.0.0.alpha-20`](https://github.com/sequelize/sequelize/pull/15374) and [`sequelize@6.29.0`](https://github.com/sequelize/sequelize/pull/15710). 

In Sequelize 7, it now produces the following:

```sql
SELECT "count(id)" AS "count" FROM "users"
```

In Sequelize 6, it throws an error explaining that we had to introduce a breaking change, and requires the user to explicitly opt-in to either the Sequelize 7 behavior (always escape) or the Sequelize 5 behavior (inline attributes that include `()` without escaping). See https://github.com/sequelize/sequelize/pull/15710 for more information.

### Mitigations

Do not use user-provided content to build your list or attributes. If you do, make sure that attribute in question actually exists on your model by checking that it exists in the `rawAttributes` property of your model first.

---

A discussion thread about this issue is open at https://github.com/sequelize/sequelize/discussions/15694
CVE: CVE-2023-22578

## References
- https://github.com/sequelize/sequelize/security/advisories/GHSA-f598-mfpv-gmfx
- https://nvd.nist.gov/vuln/detail/CVE-2023-22578
- https://github.com/sequelize/sequelize/pull/15710
- https://csirt.divd.nl/CVE-2023-22578
- https://csirt.divd.nl/DIVD-2022-00020
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/discussions/15694
- https://github.com/sequelize/sequelize/releases/tag/v6.29.0
- https://github.com/sequelize/sequelize/releases/tag/v7.0.0-alpha.20
