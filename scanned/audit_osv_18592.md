# [H] CVE-2020-28736

## Summary
Severity: High
Advisory: CVE-2020-28736
Aliases: GHSA-2c8c-84w2-j38j, PYSEC-2020-248, PYSEC-2026-2879, PYSEC-2026-2882, PYSEC-2026-2885, PYSEC-2026-735
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-30
Source: https://osv.dev/vulnerability/CVE-2020-28736
Type: osv

## Details
Plone before 5.2.3 allows XXE attacks via a feature that is protected by an unapplied permission of plone.schemaeditor.ManageSchemata (therefore, only available to the Manager role).

## References
- https://www.misakikata.com/codes/plone/python-en.html
- https://dist.plone.org/release/5.2.3/RELEASE-NOTES.txt
- https://github.com/plone/Products.CMFPlone/issues/3209
