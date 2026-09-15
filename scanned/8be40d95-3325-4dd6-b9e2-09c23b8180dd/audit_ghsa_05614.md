# [M] Pimcore is Vulnerable to Broken Access Control: Missing Function Level Authorization on "Static Routes" Listing

## Summary
Severity: Medium
Advisory: GHSA-m3r2-724c-pwgf
CVE: CVE-2026-23494
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-m3r2-724c-pwgf
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=12.0.0-RC1 <12.3.1
- Packagist: `pimcore/pimcore` — affected >=0 <11.5.14

## Details
### Summary
The application fails to enforce proper server-side authorization checks on the API endpoint responsible for reading or listing static routes. In Pimcore, static routes are custom URL patterns defined via the backend interface or the var/config/staticroutes.php file, including details like regex-based patterns, controllers, variables, and priorities. These routes are registered automatically through the PimcoreStaticRoutesBundle and integrated into the MVC routing system. Testing revealed that an authenticated backend user lacking explicit permissions was able to invoke the endpoint (e.g., GET /api/static-routes) and retrieve sensitive route configurations. This violates OWASP A01:2021 Broken Access Control, as function-level authorization is absent, allowing unauthorized access to internal routing metadata. Without validation, the endpoint exposes route structures, potentially revealing application architecture, endpoints, or custom logic intended for administrative roles only.

### Details
The backend user without permission was still able to list "Static Routes" item

### Step to Reproduce the issue
login as Admin (full permission) and clicked "Static Routes"
<img width="945" height="858" alt="Screenshot 2025-12-10 at 9 36 04 PM" src="https://github.com/user-attachments/assets/3d4ce400-9bc2-493e-a899-60d5f42ad307" />
Then, captured and saved the request:
-List API
<img width="1122" height="570" alt="Screenshot 2025-12-10 at 9 44 17 PM" src="https://github.com/user-attachments/assets/81dfb589-fe5d-46ed-b5ee-869a49c08557" />

Next, login a backend user with no permission
<img width="1219" height="744" alt="Screenshot 2025-12-10 at 9 06 12 PM" src="https://github.com/user-attachments/assets/1dada4c4-d907-4477-9773-70dea3ef5816" />

The copy the "Cookie" and "X-Pimcore-Csrf-Token"
<img width="1902" height="971" alt="Screenshot 2025-12-10 at 9 10 47 PM" src="https://github.com/user-attachments/assets/63221682-fa14-429b-8665-fc9dd8bed890" />

After that, pasted the copied "Cookie" and "X-Pimcore-Csrf-Token" to captured request

-List API
 
<img width="1132" height="829" alt="Screenshot 2025-12-10 at 9 47 27 PM" src="https://github.com/user-attachments/assets/4edea3d1-f5d9-4758-9a07-e9d484c92864" />



### Impact
Exploitation enables low-privileged users to enumerate static routes, gaining reconnaissance into URL patterns, associated controllers, and parameter handling, which could facilitate targeted attacks like path traversal, injection via exposed variables, or discovery of hidden administrative paths. In a Pimcore environment, this might expose site-specific routing for multi-tenant setups, leading to unauthorized data access, workflow manipulation, or escalation to broader system compromise. Business impacts include intellectual property leakage of custom routing logic, regulatory non-compliance (e.g., GDPR for exposed configs), and increased attack surface for chaining with other vulnerabilities.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-m3r2-724c-pwgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-23494
- https://github.com/pimcore/pimcore/pull/18893
- https://github.com/pimcore/pimcore
- https://github.com/pimcore/pimcore/releases/tag/v11.5.14
- https://github.com/pimcore/pimcore/releases/tag/v12.3.1
