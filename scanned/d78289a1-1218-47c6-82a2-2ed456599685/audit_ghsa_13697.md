# [H] Apache Superset - Elevation of Privilege

## Summary
Severity: High
Advisory: GHSA-f678-j579-4xf5
CVE: CVE-2023-40610
CWE: CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-f678-j579-4xf5
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <2.1.2

## Details
### Overview
An attacker with access to the SQL Lab and the ab_user and ab_user_role tables can elevate his privileges to become administrator.

### Details
On a more general level, diverse tables who are supposed to be only readable can be modified using the WITH … AS and RETURNING keywords.
Modification of the table key_value can also be done, which could lead to a Remote Code Execution (cf. "V7 - Insecure deserialization leading to remote code execution" report vulnerability).

### Proof of Concept
Some tables are supposed to accept only SELECT requests from the SQL tab.
- Attempt to create a new user injected_admin into the ab_user table: [PoC_1](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_1.png)

But this protection can be bypassed by using the WITH … AS () syntax with RETURNING value after the INSERT / UPDATE / DELETE query.
INSERT query accepted by the database due to the use of WITH … AS ( … RETURNING ) syntax:
  WITH a AS ( INSERT INTO ab_user (id, first_name, last_name, username, email, password) VALUES (2, ‘injected_admin’, ‘injected_admin’, ‘injected_admin’, ‘injected_admin@gmail.com’, ‘{PASSWORD_HASH}’) RETURNING id ) SELECT * FROM a;
  [PoC_2](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_2.png)
  - injected_admin added to the ab_user table: [PoC_3](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_3.png)

This method can also be used with UPDATE or DELETE request. A user with access to SELECT on the tables ab_user_role can escalate his privilege to become administrator.
- Locating the ID of the user ‘Auditeur B’, who has no rights and is not an admin. The request is done being ‘Auditeur B’: [PoC_4](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_4.png)
- Locating the rows that keep the role of the user ‘Auditeur B’. The row 36 stores the value 3, indicating the role ‘Alpha’ for ‘Auditeur B’: [PoC_5](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_5.png)
- Modification of the row 36 with an UPDATE request embedded in a WITH request: [PoC_6](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_6.png)
- ‘Auditeur B’ role has been changed to Admin: [PoC_7](https://github.com/orangecertcc/security-research/blob/main/CVE-2023-40610/PoC_7.png)

This technique can also be used to inject or modify values of the table key_value, which can potentially lead to a Remote Code Execution (cf. ...).

### Solution
#### Orange recommendation
To fix this vulnerability, we recommends reenforcing the SELECT filter to spot INSERT / UPDATE / DELETE keywords even in WITH requests.
#### Security patch
Upgrade to Superset version 2.1.2.

### References
https://nvd.nist.gov/vuln/detail/CVE-2023-40610
https://lists.apache.org/thread/jvgxpk4dbxyqtsgtl4pdgbd520rc0rot

### Credits
LEXFO for [Orange Innovation][orange]

[Orange CERT-CC][ora] at [Orange group][orange]

[ora]: <https://cert.orange.com/>
[orange]: <https://www.orange.com/>

### Timeline
**Date reported:** July 27, 2023
**Date fixed:** November 27, 2023

## References
- https://github.com/orangecertcc/security-research/security/advisories/GHSA-f678-j579-4xf5
- https://nvd.nist.gov/vuln/detail/CVE-2023-40610
- https://github.com/apache/superset
- https://lists.apache.org/thread/jvgxpk4dbxyqtsgtl4pdgbd520rc0rot
- http://www.openwall.com/lists/oss-security/2023/11/27/2
