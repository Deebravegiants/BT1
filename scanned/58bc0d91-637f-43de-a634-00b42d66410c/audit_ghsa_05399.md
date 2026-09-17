# [M] Pimcore Web2Print Tools Bundle "Favourite Output Channel Configuration" Missing Function Level Authorization

## Summary
Severity: Medium
Advisory: GHSA-4wg4-p27p-5q2r
CVE: CVE-2026-23496
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-4wg4-p27p-5q2r
Type: github-advisory

## Affected
- Packagist: `pimcore/web2print-tools-bundle` — affected >=6.0.0-RC1 <6.1.1
- Packagist: `pimcore/web2print-tools-bundle` — affected >=0 <5.2.2

## Details
### Summary
The application fails to enforce proper server-side authorization checks on the API endpoint responsible for managing "Favourite Output Channel Configurations." Testing revealed that an authenticated backend user without explicitely lacking permissions for this feature was still able to successfully invoke the endpoint and modify or retrieve these configurations. This violates the principle of least privilege and constitutes a classic example of Broken Access Control (OWASP Top 10 A01:2021). Because authorization is not validated at the function level, any authenticated user can perform actions intended only for privileged roles, leading to horizontal or vertical privilege escalation.

### Detail
The backend user without permission was still able to list, create, update "Favourite Output Channel Configuration" item

### Step to Reproduce the issue
login as Admin (full permission) and clicked "Favourite Output Channel Configurations"
<img width="949" height="860" alt="Screenshot 2025-12-10 at 8 52 55 PM" src="https://github.com/user-attachments/assets/86554e7e-86c1-469f-b09b-5f360c4507dd" />
Then, captured and saved the request:
-List API
<img width="923" height="662" alt="Screenshot 2025-12-10 at 8 55 49 PM" src="https://github.com/user-attachments/assets/21d90540-7a6b-4555-bbc0-ce74284dda67" />
-Create API
<img width="1245" height="783" alt="Screenshot 2025-12-10 at 9 01 46 PM" src="https://github.com/user-attachments/assets/38b5a771-ad17-459b-84e1-fe83c6d609a1" />
-Update API
<img width="1244" height="726" alt="Screenshot 2025-12-10 at 9 03 00 PM" src="https://github.com/user-attachments/assets/2167d48e-8941-4fff-be07-3050ffa7ad35" />

Next, login a backend user with no permission
<img width="1219" height="744" alt="Screenshot 2025-12-10 at 9 06 12 PM" src="https://github.com/user-attachments/assets/6b3981bc-4fe0-4c6e-8a5b-24523679ad4c" />
The copy the "Cookie" and "X-Pimcore-Csrf-Token"
<img width="1902" height="971" alt="Screenshot 2025-12-10 at 9 10 47 PM" src="https://github.com/user-attachments/assets/4f48f27a-6149-49fb-9209-220c2e62c25f" />
After that, pasted the copied  "Cookie" and "X-Pimcore-Csrf-Token" to captured request
- List API
<img width="1135" height="660" alt="Screenshot 2025-12-10 at 9 14 47 PM" src="https://github.com/user-attachments/assets/32ebdad2-771a-41dd-a4e6-13e8cb8ef201" />
- Create API
<img width="1140" height="697" alt="Screenshot 2025-12-10 at 9 16 43 PM" src="https://github.com/user-attachments/assets/25d5b7a9-5e96-4e7c-94cf-3c9c3d31e7f1" />
- Update API
<img width="1144" height="722" alt="Screenshot 2025-12-10 at 9 19 00 PM" src="https://github.com/user-attachments/assets/02440595-2e10-44a8-9fb7-8eb8f0aab12a" />


### Impact
Successful exploitation allows low-privileged or standard users to view, create, modify that should be restricted to specific administrative or operational roles. Depending on the sensitivity of these configurations (e.g., routing of alerts, reports, or data streams), an attacker could redirect critical outputs, suppress notifications, insert misleading channels, or gain insight into internal workflows. In regulated environments, this may result in compliance violations, operational disruption, or facilitation of further attacks through reconnaissance.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-4wg4-p27p-5q2r
- https://nvd.nist.gov/vuln/detail/CVE-2026-23496
- https://github.com/pimcore/web2print-tools/pull/108
- https://github.com/pimcore/web2print-tools/commit/7714452a04b9f9b077752784af4b8d0b05e464a1
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/web2print-tools/releases/tag/v5.2.2
- https://github.com/pimcore/web2print-tools/releases/tag/v6.1.1
