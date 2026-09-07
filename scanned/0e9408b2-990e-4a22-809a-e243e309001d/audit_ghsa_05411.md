# [M] Pimcore's Admin Classic Bundle is Missing Function Level Authorization on "Predefined Properties" Listing

## Summary
Severity: Medium
Advisory: GHSA-hqrp-m84v-2m2f
CVE: CVE-2026-23495
CWE: CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-hqrp-m84v-2m2f
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=2.0.0-RC1 <2.2.3
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.7.16

## Details
### Summary
The API endpoint for listing Predefined Properties in the Pimcore platform lacks adequate server-side authorization checks. Predefined Properties are configurable metadata definitions (e.g., name, key, type, default value) used across documents, assets, and objects to standardize custom attributes and improve editorial workflows, as documented in Pimcore's official properties guide. Testing confirmed that an authenticated backend user without explicit permissions for property management could successfully call the endpoint and retrieve the complete list of these configurations. This exemplifies Broken Access Control (OWASP Top 10 A01:2021), enabling unauthorized access to administrative features and potentially violating role-based access controls inherent to Pimcore's multi-user environment.

### Details
The backend user without permission was still able to list "Predefined Properties" item

### Step to Reproduce the issue 
login as Admin (full permission) and clicked "Predefined Properties"
<img width="1493" height="862" alt="Screenshot 2025-12-10 at 10 11 31 PM" src="https://github.com/user-attachments/assets/005d2704-347c-4aa1-b415-d52ab3794c99" />

Then, captured and saved the request:
- List API
<img width="922" height="797" alt="Screenshot 2025-12-10 at 10 39 53 PM" src="https://github.com/user-attachments/assets/2ee3e0e1-06da-442f-b2c7-0dfa8360c04a" />


Next, login a backend user with no permission
<img width="1219" height="744" alt="Screenshot 2025-12-10 at 9 06 12 PM" src="https://github.com/user-attachments/assets/1dada4c4-d907-4477-9773-70dea3ef5816" />

The copy the "Cookie" and "X-Pimcore-Csrf-Token"
<img width="1902" height="971" alt="Screenshot 2025-12-10 at 9 10 47 PM" src="https://github.com/user-attachments/assets/63221682-fa14-429b-8665-fc9dd8bed890" />

After that, pasted the copied "Cookie" and "X-Pimcore-Csrf-Token" to captured request

-List API
![Uploading Screenshot 2025-12-10 at 10.55.23 PM.png…]()


### Impact
Exploitation allows low-privileged users to enumerate all Predefined Properties, exposing internal metadata schemas, default values, and configuration details that may reveal business logic, data classification strategies, or sensitive defaults (e.g., proprietary keys or select options). In a PIM system like Pimcore, this could facilitate reconnaissance for further attacks, such as targeted data manipulation or privilege escalation, leading to unauthorized alterations of asset/object properties. For organizations handling regulated content (e.g., e-commerce catalogs under GDPR or PCI DSS), such exposure risks compliance breaches, intellectual property leakage, and operational inconsistencies from unintended property overrides.

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-hqrp-m84v-2m2f
- https://nvd.nist.gov/vuln/detail/CVE-2026-23495
- https://github.com/pimcore/admin-ui-classic-bundle/commit/98095949fbeaf11cdf4cadb2989d7454e1b88909
- https://github.com/pimcore/admin-ui-classic-bundle/releases/tag/v1.7.16
- https://github.com/pimcore/admin-ui-classic-bundle/releases/tag/v2.2.3
- https://github.com/pimcore/pimcore
