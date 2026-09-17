# [M] FacturaScripts has Insecure Parameter Handling: Unauthorized Modification of Immutable 'nick' Field

## Summary
Severity: Medium
Advisory: GHSA-pp79-hqv6-vmc3
CVE: CVE-2026-32699
CWE: CWE-284, CWE-472
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-pp79-hqv6-vmc3
Type: github-advisory

## Affected
- Packagist: `facturascripts/facturascripts` — affected >=0

## Details
### Summary
The application fails to validate the ```nick``` parameter during a ```POST``` request to the ```EditUser``` controller. Although the UI prevents editing this field, a user can bypass this restriction using a proxy to rename any account (including the Administrator). This leads to Broken Access Control and potential Audit Log Corruption.

### Details
The vulnerability exists in the user update logic. When a ```POST``` request is sent to ```/EditUser```, the backend processes the ```nick``` form-data parameter without checking if it matches the original value or if the user has the privilege to change a unique identifier that is intended to be immutable.

### PoC
***1.*** Log in to the dashboard as any user  (e.g. admin user).

***2.*** Go to your Profile  by clicking your username/avatar in the top right.

***3.*** Open Burp Suite and ensure Intercept is ON.

***5.*** Click the Save button in the UI.

***6.*** In Burp Suite, locate  ```nick```  in the body:

<img width="1915" height="1013" alt="Screenshot_2026-03-04_05_26_32" src="https://github.com/user-attachments/assets/aea4e6fd-beba-4a47-96da-8b9bd9075681" />


***7.*** Change the value admin to Vulnerable (or any other string).

***8.*** Click Forward in Burp Suite.

The application will log the user out. It is possible to now log back in using the username "Vulnerable" and the original password.

### Impact
An attacker can effectively sabotage the system’s audit trail, performing malicious actions and then renaming their account to evade detection or frame other users. This breakdown in accountability facilitates identity impersonation and risks data corruption, as internal references to the original username become orphaned, undermining the overall integrity of the multi-user environment.

### Result

#### Before 

<img width="1920" height="996" alt="Screenshot_2026-03-04_05_25_30" src="https://github.com/user-attachments/assets/3b2d34e5-a2b9-4da9-9a56-963fe1a8fd65" />

#### After

<img width="1920" height="955" alt="Screenshot_2026-03-04_05_27_00" src="https://github.com/user-attachments/assets/af1de0ef-2b55-4d29-9557-29ee26a3775a" />

## References
- https://github.com/NeoRazorX/facturascripts/security/advisories/GHSA-pp79-hqv6-vmc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-32699
- https://github.com/NeoRazorX/facturascripts
