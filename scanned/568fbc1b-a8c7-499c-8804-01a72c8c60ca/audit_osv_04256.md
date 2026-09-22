# [M] BIT-canvaslms-2021-36539

## Summary
Severity: Medium
Advisory: BIT-canvaslms-2021-36539
Aliases: CVE-2021-36539
Ecosystem: Bitnami
Published: 2024-01-31
Source: https://osv.dev/vulnerability/BIT-canvaslms-2021-36539
Type: osv

## Affected
- Bitnami: `canvaslms` — affected >=0 <2022-10-15.0.0

## Details
Instructure Canvas LMS didn't properly deny access to locked/unpublished files when the unprivileged user access the DocViewer based file preview URL (canvadoc_session_url).

## References
- https://github.com/gaukas/instructure-canvas-file-oracle
- https://github.com/instructure/canvas-lms/issues/1905
