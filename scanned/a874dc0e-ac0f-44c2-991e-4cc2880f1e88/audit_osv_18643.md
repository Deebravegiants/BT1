# [H] CVE-2020-29437

## Summary
Severity: High
Advisory: CVE-2020-29437
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-01-05
Source: https://osv.dev/vulnerability/CVE-2020-29437
Type: osv

## Details
SQL injection in the Buzz module of OrangeHRM through 4.6 allows remote authenticated attackers to execute arbitrary SQL commands via the orangehrmBuzzPlugin/lib/dao/BuzzDao.php loadMorePostsForm[profileUserId] parameter to the buzz/loadMoreProfile endpoint.

## References
- https://github.com/orangehrm/orangehrm/issues/695
- https://github.com/orangehrm/orangehrm/releases
- https://github.com/orangehrm/orangehrm/pull/699
- https://www.horizon3.ai/disclosures/orangehrm-sqli.html
