# [H] JLSEC-2026-180

## Summary
Severity: High
Advisory: JLSEC-2026-180
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/JLSEC-2026-180
Type: osv

## Affected
- Julia: `MongoC_jll` — affected >=0 <1.28.1+0

## Details
Incorrect validation of files loaded from a local untrusted directory may allow local privilege escalation if the underlying operating systems is Windows. This may result in the application executing arbitrary behaviour determined by the contents of untrusted files. This issue affects MongoDB Server v5.0 versions prior to 5.0.27, MongoDB Server v6.0 versions prior to 6.0.16, MongoDB Server v7.0 versions prior to 7.0.12, MongoDB Server v7.3 versions prior 7.3.3, MongoDB C Driver versions prior to 1.26.2 and MongoDB PHP Driver versions prior to 1.18.1.

Required Configuration:

Only environments with Windows as the underlying operating system is affected by this issue

## References
- https://jira.mongodb.org/browse/CDRIVER-5650
- https://jira.mongodb.org/browse/PHPC-2369
- https://jira.mongodb.org/browse/SERVER-93211
