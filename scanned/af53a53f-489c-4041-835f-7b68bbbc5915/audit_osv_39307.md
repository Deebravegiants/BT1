# [H] Himmelblau: Authentication Bypass via Cross-User Local Session Impersonation in Device Authorization Grant (DAG) Flow

## Summary
Severity: High
Advisory: CVE-2026-45108
Aliases: GHSA-pmxh-j4r6-88mv
CVSS: 8.4 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-05-27
Source: https://osv.dev/vulnerability/CVE-2026-45108
Type: osv

## Details
Himmelblau is an interoperability suite for Microsoft Azure Entra ID and Intune. From 2.0.0 to before 3.1.5 and 2.3.11, Himmelblau contained an authentication bypass vulnerability in the Device Authorization Grant (DAG) flow that allowed a user within the same Entra ID domain to obtain a local Unix session as another user by providing their own valid credentials. The vulnerability existed in the token_validate function, which validated domain aliases for legitimate multi-domain scenarios but failed to verify that the local part (username) of the authenticated user's UPN matched the requested account username. The function only compared domains, not the complete usernames. This vulnerability is fixed in 3.1.5 and 2.3.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45108.json
- https://github.com/himmelblau-idm/himmelblau/security/advisories/GHSA-pmxh-j4r6-88mv
- https://nvd.nist.gov/vuln/detail/CVE-2026-45108
