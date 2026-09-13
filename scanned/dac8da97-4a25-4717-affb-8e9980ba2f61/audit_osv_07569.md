# [M] Apache Superset: Metadata db write access can lead to remote code execution

## Summary
Severity: Medium
Advisory: BIT-superset-2023-37941
Aliases: CVE-2023-37941, GHSA-fj4x-m62j-wvwg, PYSEC-2026-1175
Ecosystem: Bitnami
Published: 2025-02-05
Source: https://osv.dev/vulnerability/BIT-superset-2023-37941
Type: osv

## Affected
- Bitnami: `superset` — affected >=1.5.0 <2.1.1

## Details
If an attacker gains write access to the Apache Superset metadata database, they could persist a specifically crafted Python object that may lead to remote code execution on Superset's web backend.

The Superset metadata db is an 'internal' component that is typically 
only accessible directly by the system administrator and the superset 
process itself. Gaining access to that database should
 be difficult and require significant privileges.

This vulnerability impacts Apache Superset versions 1.5.0 up to and including 2.1.0. Users are recommended to upgrade to version 2.1.1 or later.

## References
- http://packetstormsecurity.com/files/175094/Apache-Superset-2.0.0-Remote-Code-Execution.html
- https://lists.apache.org/thread/6qk1zscc06yogxxfgz2bh2bvz6vh9g7h
- https://nvd.nist.gov/vuln/detail/CVE-2023-37941
