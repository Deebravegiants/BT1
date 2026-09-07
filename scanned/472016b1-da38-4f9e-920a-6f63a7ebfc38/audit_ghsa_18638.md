# [M] Shopware exposes sensitive user information via CSV export mapping

## Summary
Severity: Medium
Advisory: GHSA-27c9-vp3w-6ww8
CWE: CWE-212
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-21
Source: https://github.com/advisories/GHSA-27c9-vp3w-6ww8
Type: github-advisory

## Affected
- Packagist: `shopware/platform` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/platform` — affected >=0 <6.6.10.7
- Packagist: `shopware/core` — affected >=6.7.0.0 <6.7.3.1
- Packagist: `shopware/core` — affected >=0 <6.6.10.7

## Details
### Impact
Malicious actors can exploit this finding to export sensitive customer information from a Shopware application, including password hashes and password reset tokens. In SaaS deployments, this primarily affects customer accounts. In on-premise deployments, however, it also includes the hashes and recovery tokens of administrator-level accounts, which increases
the potential impact. 
This risk is noteworthy because users may reuse the same or similar passwords across different services. In such cases, exposed hashes could allow attackers to recover credentials that might also be valid outside of Shopware.

#### Description
Sensitive information disclosure occurs when an application inadvertently displays sensitive information to its users. Depending on the context, websites can leak all kinds of information including:
• Data regarding other users, such as usernames and/or e-mail addresses
• Sensitive commercial data such as customer names
• Technical details about the website and/or the underlying infrastructure
Disclosing technical details, such as detailed version information, allows malicious actors to look for targeted vulnerabilities and/or misconfigurations in the application or in the underlying infrastructure. In addition, an application is more likely to be targeted by attacks that specifically target a particular version of the software used.

#### Applicability
The Shopware application exposes sensitive information to users within the export section.
The Shopware application allows admins to import and export data within the application. To do this import/export profiles can be created. These profiles tell the application which tables within the database map to which columns in the generated file. During testing it was noticed that sensitive information such as password hashes or reset codes can also be included within the export. This can be done by creating a custom mapping that includes these fields within the export.
To exploit this vulnerability, an account with permissions to create import/export profiles and to create exports, is required.

#### Reproduction 
To reproduce this vulnerability, the steps below can be followed.
1. Log in to Shopware application with an admin account capable of creating import/export profiles and creating exports
2. Create a new import/export profile
3. Add a new mapping for the ‘password’ database entry
4. Create an export using the new profile
5. Notice that the password hashes of the users are available within the export file.

## References
- https://github.com/shopware/shopware/security/advisories/GHSA-27c9-vp3w-6ww8
- https://github.com/shopware/shopware/commit/c2c98050aff7b90fe7232f6dac9b6b7143183083
- https://github.com/shopware/shopware
