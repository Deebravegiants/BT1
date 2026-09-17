# [M] Msa-24-0003: h5p attempts report did not respect activity group settings

## Summary
Severity: Medium
Advisory: BIT-moodle-2024-25980
Aliases: CVE-2024-25980, GHSA-cp8m-h777-g4p3
Ecosystem: Bitnami
Published: 2024-03-31
Source: https://osv.dev/vulnerability/BIT-moodle-2024-25980
Type: osv

## Affected
- Bitnami: `moodle` — affected >=4.3.0 <4.3.3

## Details
Separate Groups mode restrictions were not honored in the H5P attempts report, which would display users from other groups. By default this only provided additional access to non-editing teachers.

## References
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-80501
- https://bugzilla.redhat.com/show_bug.cgi?id=2264096
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KXGBYJ43BUEBUAQZU3DT5I5A3YLF47CB/
- https://moodle.org/mod/forum/discuss.php?d=455636
- https://nvd.nist.gov/vuln/detail/CVE-2024-25980
