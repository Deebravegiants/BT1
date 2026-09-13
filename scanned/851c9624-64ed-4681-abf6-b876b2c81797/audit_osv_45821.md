# [H] JLSEC-2026-37

## Summary
Severity: High
Advisory: JLSEC-2026-37
Ecosystem: Julia
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-37
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <14.3.0+0

## Details
A flaw was found in PostgreSQL. There is an issue with incomplete efforts to operate safely when a privileged user is maintaining another user's objects. The Autovacuum, REINDEX, CREATE INDEX, REFRESH MATERIALIZED VIEW, CLUSTER, and `pg_amcheck` commands activated relevant protections too late or not at all during the process. This flaw allows an attacker with permission to create non-temporary objects in at least one schema to execute arbitrary SQL functions under a superuser identity.

## References
- https://access.redhat.com/security/cve/CVE-2022-1552
- https://bugzilla.redhat.com/show_bug.cgi?id=2081126
- https://security.gentoo.org/glsa/202211-04
- https://security.netapp.com/advisory/ntap-20221104-0005/
- https://www.postgresql.org/about/news/postgresql-143-137-1211-1116-and-1021-released-2449/
- https://www.postgresql.org/support/security/CVE-2022-1552/
