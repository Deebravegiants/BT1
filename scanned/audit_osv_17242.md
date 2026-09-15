# [H] CVE-2020-13978

## Summary
Severity: High
Advisory: CVE-2020-13978
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-06-09
Source: https://osv.dev/vulnerability/CVE-2020-13978
Type: osv

## Details
Monstra CMS 3.0.4 allows an attacker, who already has administrative access to modify .chunk.php files on the Edit Chunk screen, to execute arbitrary OS commands via the Theme Module by visiting the admin/index.php?id=themes&action=edit_chunk URI. NOTE: there is no indication that the Edit Chunk feature was intended to prevent an administrator from using PHP's exec feature

## References
- https://github.com/monstra-cms/monstra/issues/464
