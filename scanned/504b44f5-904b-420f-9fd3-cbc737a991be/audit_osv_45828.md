# [H] JLSEC-2026-38

## Summary
Severity: High
Advisory: JLSEC-2026-38
Ecosystem: Julia
CVSS: 8.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/JLSEC-2026-38
Type: osv

## Affected
- Julia: `LibPQ_jll` — affected >=0 <16.0.0+0

## Details
A vulnerability was found in PostgreSQL. This attack requires permission to create non-temporary objects in at least one schema, the ability to lure or wait for an administrator to create or update an affected extension in that schema, and the ability to lure or wait for a victim to use the object targeted in CREATE OR REPLACE or CREATE IF NOT EXISTS. Given all three prerequisites, this flaw allows an attacker to run arbitrary code as the victim role, which may be a superuser.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=2113825
- https://security.gentoo.org/glsa/202211-04
- https://www.postgresql.org/about/news/postgresql-145-138-1212-1117-1022-and-15-beta-3-released-2496/
