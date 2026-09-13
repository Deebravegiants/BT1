# [M] phpMyFAQ User Removal Page Allows Spoofing Of User Details

## Summary
Severity: Medium
Advisory: GHSA-6648-6g96-mg35
CVE: CVE-2024-22202
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-6648-6g96-mg35
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <3.2.5

## Details
### Summary
phpMyFAQ's user removal page allows an attacker to spoof another user's detail, and in turn make a compelling phishing case for removing another user's account.

### Details
phpMyFAQ's user removal page allows an attacker to spoof another user's detail, and in turn make a compelling phishing case for removing another user's account. Whilst the front-end of this page doesn't allow changing the form details, an attacker can utilize a proxy to intercept this request and submit other data. Upon submitting this form, an email is sent to the administrator informing them that this user wants to delete their account. An administrator has no way of telling the difference between the actual user wishing to delete their account or the attacker issuing this for an account they do not control.

### PoC
We are logged in as `hacker` and visit `/user/request-removal`. This brings us to the following page. We are not able to change the `username`, `Your name` and `Your email address` fields on this page.
![image](https://user-images.githubusercontent.com/44903767/296202382-9e6d6409-3ffb-4983-8895-9903e7dfc663.png)

However, we intercept this request using a proxy tool such as BurpSuite.
![image](https://user-images.githubusercontent.com/44903767/296202522-dd80fe87-e7b7-4fe2-97be-dca03289f506.png)

We can now edit the request before sending it. We change the fields mentioned above to the details of another user, and send the request.
![image](https://user-images.githubusercontent.com/44903767/296202705-fa8fd3f8-1417-457e-9d6e-7e4ba0f8744a.png)

This results in the following email being sent to the administrator. For them, it looks like the victim wants to delete their account.
![image](https://user-images.githubusercontent.com/44903767/296202935-a5c48e0b-f93e-488a-9716-4f93889100a7.png)

### Impact
The impact of this vulnerability is that administrators cannot trust the emails sent by the platform. An attacker can easily make a compelling case to perform phishing and get victim accounts deleted.

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-6648-6g96-mg35
- https://nvd.nist.gov/vuln/detail/CVE-2024-22202
- https://github.com/thorsten/phpMyFAQ/commit/1348dcecdaec5a5714ad567c16429432417b534d
- https://github.com/thorsten/phpMyFAQ
- https://www.phpmyfaq.de/security/advisory-2024-02-05
