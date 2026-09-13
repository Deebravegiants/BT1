# [M] SQL injection in sql_optimize.py optimize_sqltuningadvisor method in Archery - GHSL-2022-107

## Summary
Severity: Medium
Advisory: CVE-2023-30556
Aliases: GHSA-6pv9-9gq7-hr68
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-04-18
Source: https://osv.dev/vulnerability/CVE-2023-30556
Type: osv

## Details
Archery is an open source SQL audit platform. The Archery project contains multiple SQL injection vulnerabilities, that may allow an attacker to query the connected databases. Affected versions are subject to SQL injection in the `optimize_sqltuningadvisor` method of `sql_optimize.py`. User input coming from the `db_name` parameter value in `sql_optimize.py` is passed to the `sqltuningadvisor` method in `oracle.py`for execution. To mitigate escape the variables accepted via user input when used in `sql_optimize.py`. Users may also use prepared statements when dealing with SQL as a mitigation for this issue. This issue is also indexed as `GHSL-2022-107`.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30556.json
- https://github.com/hhyo/Archery/security/advisories/GHSA-6pv9-9gq7-hr68
- https://nvd.nist.gov/vuln/detail/CVE-2023-30556
