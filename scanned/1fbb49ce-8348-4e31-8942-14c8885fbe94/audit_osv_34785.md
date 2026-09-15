# [M] Rallly Has an IDOR Vulnerability in Vote Update Endpoint Allows Unauthorized Manipulation of Participant Votes

## Summary
Severity: Medium
Advisory: CVE-2025-65028
Aliases: GHSA-pchc-v5hg-f5gp
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65028
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an insecure direct object reference (IDOR) vulnerability allows any authenticated user to modify other participants’ votes in polls without authorization. The backend relies solely on the participantId parameter to identify which votes to update, without verifying ownership or poll permissions. This allows an attacker to alter poll results in their favor, directly compromising data integrity. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65028.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-pchc-v5hg-f5gp
- https://nvd.nist.gov/vuln/detail/CVE-2025-65028
