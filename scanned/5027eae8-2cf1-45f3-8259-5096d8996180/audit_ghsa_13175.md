# [M] Strapi may leak sensitive user information, user reset password, tokens via content-manager views

## Summary
Severity: Medium
Advisory: GHSA-v8gg-4mq2-88q4
CVE: CVE-2023-36472
CWE: CWE-200
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-13
Source: https://github.com/advisories/GHSA-v8gg-4mq2-88q4
Type: github-advisory

## Affected
- npm: `@strapi/plugin-content-manager` — affected >=0 <4.11.7
- npm: `@strapi/admin` — affected >=0 <4.11.7
- npm: `@strapi/utils` — affected >=0 <4.11.7

## Details
### Summary
I can get access to user  reset password tokens if I have the configure view permissions
![b37a6fd9eae06027e7d91266f1908a3d](https://user-images.githubusercontent.com/34578426/246782921-fbc007d3-ffec-45de-a1f1-a4287cd507ac.png)
![6c1da5b3bfbb3bca97c8d064be0ecb05](https://user-images.githubusercontent.com/34578426/246783044-7d716dde-6f27-4d01-9521-42720c6ce92e.gif)

### Details
/content-manager/relations route does not remove private fields or ensure that they can't be selected

### PoC
Install fresh strapi instance
start up strapi and create an account
create a new content-type
give the content-type a relation with admin users and save
go to Admin panel roles Author and then plugins.
Enable for content-manager collection types the configure view
In the collection time now only give them access to the collection you created for this.
Create a new admin user account with the Author role
Log out and request a password reset for the main admin user.
Login on the newly created account
go to the collection type you created for this test and click the create new entry button,
click in the create new entry view on configure view.
select the admin user relation we created click on resetPasswordToken
Now go back to the create an entry view and when selection the relation we created we now see the reset tokken

### Impact
Impact is that the none admin user now has the reset token of the admin users account and can resets its password using that to escalate his privilege's

Still you need the configure view permission to be able to escalate your privilege's

## References
- https://github.com/strapi/strapi/security/advisories/GHSA-v8gg-4mq2-88q4
- https://nvd.nist.gov/vuln/detail/CVE-2023-36472
- https://github.com/strapi/strapi
- https://github.com/strapi/strapi/releases/tag/v4.11.7
