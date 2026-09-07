# [M] Craft CMS vulnerable to stored XSS in breadcrumb list and title fields

## Summary
Severity: Medium
Advisory: GHSA-28h4-788g-rh42
CVE: CVE-2024-45406
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-09-09
Source: https://github.com/advisories/GHSA-28h4-788g-rh42
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0 <5.1.2

## Details
### Summary
Multiple Stored XSS can be triggered by the breadcrumb list and title fields with user input.

### Details
1. In the **/admin/categories** page, category title isn't sanitized and triggered xss.
2. In the category edit page under the **/admin/categories/**, category title in breadcrumb list isn't sanitized and triggered xss.
3. In the **/admin/entries** page, entry title isn't sanitized and triggered xss.
4. In the entry edit page under the **/admin/entries/**, entry title in breadcrumb list isn't sanitized and triggered xss.
5. In the **/admin/myaccount** and pages under it, username or full name in breadcrumb list isn't sanitized and triggered xss.

### Impact
Malicious users can tamper with the control panel.

### PoC
#### 1. In the **/admin/categories** page, category title isn't sanitized and triggered xss.
```
1. Access to the Settings -> Categories ( /admin/settings/categories )
2. Create new category group
3. Access to the Categories page ( /admin/categories/ )
4. Push the New category button
5. Input the Title column : xss<script>alert('xss')</script>
6. Push the Create Category or Save button
7. Access to the Categories page again and it triggers xss
``` 
![image](https://github.com/craftcms/cms/assets/83068208/a1b2890e-731b-4fc4-b189-26591f4486fd)
![image](https://github.com/craftcms/cms/assets/83068208/4e0f35c7-fbb0-4d38-a0b5-9e28750ff706)
![image](https://github.com/craftcms/cms/assets/83068208/e046b9db-d83c-4f81-ad91-165c5afedeb9)

#### 2. In the category edit page under the **/admin/categories/**, category title in breadcrumb list isn't sanitized and triggered xss.
```
1. Access to the Settings -> Categories ( /admin/settings/categories )
2. Create new category group
3. Access to the Categories page ( /admin/categories/ )
4. Push the New category button
5. Input the Title column : xss<script>alert('xss')</script>
6. Push the Create Category or Save button
7. Access to the Category edit page again and it triggers xss
``` 
![image](https://github.com/craftcms/cms/assets/83068208/a1b2890e-731b-4fc4-b189-26591f4486fd)
![image](https://github.com/craftcms/cms/assets/83068208/f7543a11-58eb-4099-9ee2-3461816c52ea)
![image](https://github.com/craftcms/cms/assets/83068208/f01bbb80-4417-42ca-bf51-b38860f6c74a)

#### 3. In the **/admin/entries** page, entry title isn't sanitized and triggered xss.
```
1. Access to the Settings -> Entry Types ( /admin/settings/entry-types )
2. Create new entry type
3. Access to the Settings -> Sections ( /admin/settings/sections )
4. Create new section
5. Access to the Entries page ( /admin/entries )
6. Push the New entry button
7. Input the Title column : xss<script>alert('xss')</script>
8. Push the Create entry or Save button
9. Access to the Entries page again and it triggers xss
``` 
![image](https://github.com/craftcms/cms/assets/83068208/ba700899-947f-4421-a1b7-3f0cc2c0da30)
![image](https://github.com/craftcms/cms/assets/83068208/b255a999-e48c-46be-b732-4482ea9cee9a)
![image](https://github.com/craftcms/cms/assets/83068208/445d8e0c-71b6-49c7-8f4a-37541dcc9c85)

#### 4. In the entry edit page under the **/admin/entries/**, entry title in breadcrumb list isn't sanitized and triggered xss.
```
1. Access to the Settings -> Entry Types ( /admin/settings/entry-types )
2. Create new entry type
3. Access to the Settings -> Sections ( /admin/settings/sections )
4. Create new section
5. Access to the Entries page ( /admin/entries )
6. Push the New entry button
7. Input the Title column : xss<script>alert('xss')</script>
8. Push the Create entry or Save button
9. Access to the Entriy edit page again and it triggers xss
``` 
![image](https://github.com/craftcms/cms/assets/83068208/ba700899-947f-4421-a1b7-3f0cc2c0da30)
![image](https://github.com/craftcms/cms/assets/83068208/a59a122b-b9e7-4695-be13-eb8a1c2d36df)
![image](https://github.com/craftcms/cms/assets/83068208/b0d27446-7ac6-47e7-ac02-20c924698b13)

#### 5. In the **/admin/myaccount** and pages under it, username or full name in breadcrumb list isn't sanitized and triggered xss.
```
1. Access to the My Account Page ( /admin/myaccount )
2. Input the Full Name column : xss<script>alert('xss')</script>
3. Push the the Save button
4. Access to the My Account page ( /admin/myaccount ) or pages under it ( /admin/myaccount/addresses , /admin/myaccount/preferences , etc.) and it triggers xss
``` 
![image](https://github.com/craftcms/cms/assets/83068208/3be45bdd-0757-42a8-bc5d-320ab2339fd0)
![image](https://github.com/craftcms/cms/assets/83068208/e1be7446-1c54-42bc-af9a-a8ac81a2d7bf)
![image](https://github.com/craftcms/cms/assets/83068208/5fa06b26-fecd-40f5-bc8b-171f881f8a2a)

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-28h4-788g-rh42
- https://nvd.nist.gov/vuln/detail/CVE-2024-45406
- https://github.com/craftcms/cms/commit/b7348942f8131b3868ec6f46d615baae50151bb8
- https://github.com/craftcms/cms
