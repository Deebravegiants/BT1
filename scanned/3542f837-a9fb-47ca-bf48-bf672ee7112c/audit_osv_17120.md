# [M] CVE-2020-12687

## Summary
Severity: Medium
Advisory: CVE-2020-12687
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-05-07
Source: https://osv.dev/vulnerability/CVE-2020-12687
Type: osv

## Details
An issue was discovered in Serpico before 1.3.3. The /admin/attacments_backup endpoint can be requested by non-admin authenticated users. This means that an attacker with a user account can retrieve all of the attachments of all users (including administrators) from the database.

## References
- https://github.com/SerpicoProject/Serpico/commit/0b8600414976a5ad733604c7b1428071baf239c2
- https://github.com/SerpicoProject/Serpico/releases/tag/1.3.3
