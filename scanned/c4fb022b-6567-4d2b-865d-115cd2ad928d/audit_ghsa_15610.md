# [C] H2O.ai H2O vulnerable to deserialization attacks via a JDBC Connection URL

## Summary
Severity: Critical
Advisory: GHSA-hrmc-jmp7-mpm2
CVE: CVE-2024-45758
CWE: CWE-502
Ecosystem: Maven, PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-06
Source: https://github.com/advisories/GHSA-hrmc-jmp7-mpm2
Type: github-advisory

## Affected
- Maven: `ai.h2o:h2o-core` — affected >=0
- PyPI: `h2o` — affected >=0

## Details
H2O.ai H2O through 3.46.0.4 allows attackers to arbitrarily set the JDBC URL, leading to deserialization attacks, file reads, and command execution. Exploitation can occur when an attacker has access to post to the ImportSQLTable URI with a JSON document containing a connection_url property with any typical JDBC Connection URL attack payload such as one that uses queryInterceptors.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-45758
- https://github.com/h2oai/h2o-3/issues/16425
- https://github.com/h2oai/h2o-3/issues/16622
- https://github.com/h2oai/h2o-3/pull/16624
- https://github.com/h2oai/h2o-3/commit/f714edd6b8429c7a7211b779b6ec108a95b7382d
- https://gist.github.com/AfterSnows/c24ca3c26dc89ab797e610e92a6a9acb
- https://github.com/h2oai/h2o-3
- https://spear-shield.notion.site/Unauthenticated-Remote-Code-Execution-via-Unrestricted-JDBC-Connection-87a958a4874044199cbb86422d1f6068
