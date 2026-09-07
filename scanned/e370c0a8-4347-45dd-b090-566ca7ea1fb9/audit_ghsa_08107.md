# [M]  Craft Commerce has Stored XSS in Inventory Location Address Leading to Potential Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-wq2m-r96q-crrf
CVE: CVE-2026-25490
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:P/VC:N/VI:N/VA:N/SC:L/SI:H/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-wq2m-r96q-crrf
Type: github-advisory

## Affected
- Packagist: `craftcms/commerce` — affected >=5.0.0-RC1 <5.5.2
- Packagist: `craftcms/commerce` — affected >=4.0.0-RC1 <4.10.1

## Details
## Summary
A stored XSS vulnerability in Craft Commerce allows attackers to execute malicious JavaScript in an administrator’s browser. This occurs because the 'Address Line 1' field in Inventory Locations is not properly sanitized before being displayed in the admin panel.

## Proof of Concept

### Required Permissions
- General permissions:
	- Access the control panel
	- Access Craft Commerce
- Craft Commerce permissions:
	- Manage inventory locations
- An active administrator elevated session

<img width="887" height="832" alt="req-perms" src="https://github.com/user-attachments/assets/7a9a5ef6-4fc3-4af1-8ded-08861ead0b7e" />


### Steps to Reproduce
1. Log in to the Admin Panel with the attacker account with the permissions mentioned above.
2. Navigate to **Commerce** -> **Inventory Locations** -> **Default** (`/admin/commerce/inventory-locations/1`).
3. In the **Address Line 1** field, enter the following payload:
```html
<img src=x onerror="alert(document.domain)">
```
4. Click **Save** and you'll be redirected back to the **Inventory Locations** page.
5. Notice the alert proving JavaScript execution.
<img width="1814" height="606" alt="alert-poc" src="https://github.com/user-attachments/assets/f08aed21-a676-4dee-85a8-d195bab85685" />



### Privilege Escalation to Administrator:
1. Do the same steps above, but replace the payload with a malicious one.
2. The following payload elevates the attacker’s account to Admin if there’s already an elevated session, replace the `<UserID>` with the attacker id:
```html
<img src=x onerror="fetch('/admin/users/<UserID>/permissions',{method:'POST',body:`CRAFT_CSRF_TOKEN=${Craft.csrfTokenValue}&userId=<UserID>&admin=1&action=users/save-permissions`,headers:{'content-type':'application/x-www-form-urlencoded'}})">
```
3. In another browser, log in as an admin & go to the vulnerable page (Inventory Location page).
4. Go back to the attacker account & notice it now has admin status.

The privilege escalation requires an elevated session. In a real-world scenario, an attacker can automate the process by forcing a logout if the victim’s session is stale; upon re-authentication, the stored XSS payload executes within a fresh elevated session to complete the attack.

Or even easier (and smarter), an attacker (using the XSS) can create a fake 'Session Expired' login modal overlay. Since it’s on the trusted domain, administrators will likely enter their credentials, sending them directly to the attacker.

### Resources:

https://github.com/craftcms/commerce/commit/fa273330807807d05b564d37c88654cd772839ee

## References
- https://github.com/craftcms/commerce/security/advisories/GHSA-wq2m-r96q-crrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25490
- https://github.com/craftcms/commerce/commit/fa273330807807d05b564d37c88654cd772839ee
- https://github.com/craftcms/commerce
- https://github.com/craftcms/commerce/releases/tag/4.10.1
- https://github.com/craftcms/commerce/releases/tag/5.5.2
