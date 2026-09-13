# [H] CVE-2018-15886

## Summary
Severity: High
Advisory: CVE-2018-15886
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-09-10
Source: https://osv.dev/vulnerability/CVE-2018-15886
Type: osv

## Details
Monstra CMS 3.0.4 does not properly restrict modified Snippet content, as demonstrated by the admin/index.php?id=snippets&action=edit_snippet&filename=google-analytics URI, which allows attackers to execute arbitrary PHP code by placing this code after a <?php substring.

## References
- https://github.com/monstra-cms/monstra/issues/455
