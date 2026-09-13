# [H] CVE-2025-4581

## Summary
Severity: High
Advisory: CVE-2025-4581
Aliases: GHSA-6v93-frf9-2rp8
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2025-08-09
Source: https://osv.dev/vulnerability/CVE-2025-4581
Type: osv

## Details
Liferay Portal 7.4.0 through 7.4.3.132, and Liferay DXP 2025.Q1.0 through 2025.Q1.4 ,2024.Q4.0 through 2024.Q4.7, 2024.Q3.1 through 2024.Q3.13, 2024.Q2.0 through 2024.Q2.13, 2024.Q1.1 through 2024.Q1.15, 7.4 GA through update 92 allows a pre-authentication blind SSRF vulnerability in the portal-settings-authentication-opensso-web due to improper validation of user-supplied URLs. An attacker can exploit this issue to force the server to make arbitrary HTTP requests to internal systems, potentially leading to internal network enumeration or further exploitation.

## References
- https://liferay.dev/portal/security/known-vulnerabilities/-/asset_publisher/jekt/content/CVE-2025-4581
