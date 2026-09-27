# [H] Grav has Broken Access Control which allows an Editor to modify the page's YAML Frontmatter to alter form processing actions

## Summary
Severity: High
Advisory: GHSA-v8x2-fjv7-8hjh
CVE: CVE-2025-66301
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-02
Source: https://github.com/advisories/GHSA-v8x2-fjv7-8hjh
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.8.0-beta.27

## Details
### Summary
Due to a broken access control vulnerability in the `/admin/pages/{page_name}` endpoint, an editor ( user with full permissions to pages ) can change the functionality of a form after submission.

### Details
Due to improper authorization checks when modifying critical fields on a POST request to `/admin/pages/{page_name}`, an editor with only permissions to change basic content on the form is now able to change the functioning of the form through modifying the content of the `data[_json][header][form]` which is the YAML frontmatter which includes the `process` section which dictates what happens after a user submits the form which include some important actions that could lead to further vulnerabilities.

### PoC

- Have Admin and Form plugins installed
- Connect to panel as admin, create user and give him permission for pages all
- Now connect as that user and notice you cant edit any process field in the panel
- Change anything in the content of the form and save
- Intercept the request:
![image](https://github.com/user-attachments/assets/a66767d9-648e-45b5-9031-4a15bee3072a)

- Now modify the field `data[_json][header][form] with the following payload URL-encoded not like this:
```
{"name":"ssti-test 2","fields":{"name":{"type":"text","label":"Name","required":true}},"buttons":{"submit":{"type":"submit","value":"Submit"}},"process":[{"message":"{{ evaluate_twig(form.value('name')) }}"}]}
```

- Change the field and forward it:
![image](https://github.com/user-attachments/assets/dd5f95d7-c61f-4fc0-9e9a-e67825f20aea)

Request goes through and changes have been made to the form.
![image](https://github.com/user-attachments/assets/42a77e10-571b-43a2-8410-14d82dba28e5)

### Impact

- Attacker can modify submission logic of the form which leads to changing redirect value, email sending, changing template, breaking out of the Twig sandbox potentially executing code...

### Fix recommendation

- Implement proper authorization checks to such requests especially when it contains fields user shouldn't be able to modify based on his role.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-v8x2-fjv7-8hjh
- https://nvd.nist.gov/vuln/detail/CVE-2025-66301
- https://github.com/getgrav/grav
