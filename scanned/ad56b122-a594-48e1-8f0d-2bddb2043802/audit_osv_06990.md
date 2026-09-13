# [M] Msa-24-0004: forum export did not respect activity group settings

## Summary
Severity: Medium
Advisory: BIT-moodle-2024-25981
Aliases: CVE-2024-25981, GHSA-jfrg-9hpq-9hvp
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-moodle-2024-25981
Type: osv

## Affected
- Bitnami: `moodle` — affected >=4.3.0 <4.3.3

## Details
Separate Groups mode restrictions were not honored when performing a forum export, which would export forum data for all groups. By default this only provided additional access to non-editing teachers.

## References
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-80504
- https://bugzilla.redhat.com/show_bug.cgi?id=2264097
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KXGBYJ43BUEBUAQZU3DT5I5A3YLF47CB/
- https://moodle.org/mod/forum/discuss.php?d=455637
- https://nvd.nist.gov/vuln/detail/CVE-2024-25981
