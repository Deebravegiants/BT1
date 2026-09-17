# [C] RevelaCode exposes Sensitive MongoDB Atlas URI in .env (potential credential leak)

## Summary
Severity: Critical
Advisory: CVE-2025-54428
Aliases: GHSA-m253-qvcr-cr48
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-28
Source: https://osv.dev/vulnerability/CVE-2025-54428
Type: osv

## Details
RevelaCode is an AI-powered faith-tech project that decodes biblical verses, prophecies and global events into accessible language. In versions below 1.0.1, a valid MongoDB Atlas URI with embedded username and password was accidentally committed to the public repository. This could allow unauthorized access to production or staging databases, potentially leading to data exfiltration, modification, or deletion. This is fixed in version 1.0.1. Workarounds include: immediately rotating credentials for the exposed database user, using a secret manager (like Vault, Doppler, AWS Secrets Manager, etc.) instead of storing secrets directly in code, or auditing recent access logs for suspicious activity.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/54xxx/CVE-2025-54428.json
- https://github.com/musombi123/RevelaCode-Backend/security/advisories/GHSA-m253-qvcr-cr48
- https://nvd.nist.gov/vuln/detail/CVE-2025-54428
- https://github.com/musombi123/RevelaCode-Backend/commit/95005cf4bacf1b005aef9d4b8e85237c98492d83
