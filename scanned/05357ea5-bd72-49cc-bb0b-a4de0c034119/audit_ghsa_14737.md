# [M] Vitess allows HTML injection in /debug/querylogz & /debug/env

## Summary
Severity: Medium
Advisory: GHSA-7mwh-q3xm-qh6p
CVE: CVE-2024-53257
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-12-03
Source: https://github.com/advisories/GHSA-7mwh-q3xm-qh6p
Type: github-advisory

## Affected
- Go: `vitess.io/vitess` — affected >=0.21.0-rc1 <0.21.1
- Go: `vitess.io/vitess` — affected >=0.20.0-rc1 <0.20.4
- Go: `vitess.io/vitess` — affected >=0 <0.19.8

## Details
### Summary

The `/debug/querylogz` and `/debug/env` pages for `vtgate` and `vttablet` do not properly escape user input. The result is that queries executed by Vitess can write HTML into the monitoring page at will.

### Details

These pages are rendered using `text/template` instead of rendering with a proper HTML templating engine.

### PoC

Execute any query where part of it is HTML markup, for example as part of a string. To make it easier to observe you might want to make sure the query takes a few seconds to complete, giving you time to refresh the status page. 

Example query that can trigger the issue:

```sql
UPDATE users
SET
    email = CONCAT("<img src=https://cataas.com/cat/says/oops>", users.idUser, "@xxx")
WHERE
    email NOT LIKE '%xxx%' AND email != "demo@xxx.com"
```

Result: 

![image](https://github.com/user-attachments/assets/c583816b-157c-474e-bbed-152b3dc0372f)

### Impact

Anyone looking at the Vitess status page is affected. This would normally be owners / administrators of the Vitess cluster.

Anyone that can influence what text show up in queries can trigger it. This would normally be pretty much everybody interacting with a system that uses Vitess as a backend.

## References
- https://github.com/vitessio/vitess/security/advisories/GHSA-7mwh-q3xm-qh6p
- https://nvd.nist.gov/vuln/detail/CVE-2024-53257
- https://github.com/vitessio/vitess/commit/2b71d1b5f8ca676beeab2875525003cd45096217
- https://github.com/vitessio/vitess
