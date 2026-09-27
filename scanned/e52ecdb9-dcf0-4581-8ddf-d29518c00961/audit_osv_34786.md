# [H] Rallly Has an IDOR Vulnerability in Participant Deletion Endpoint Allows Unauthorized Removal of Poll Participants

## Summary
Severity: High
Advisory: CVE-2025-65029
Aliases: GHSA-f8jc-6746-ww95
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-11-19
Source: https://osv.dev/vulnerability/CVE-2025-65029
Type: osv

## Details
Rallly is an open-source scheduling and collaboration tool. Prior to version 4.5.4, an insecure direct object reference (IDOR) vulnerability allows any authenticated user to delete arbitrary participants from polls without ownership verification. The endpoint relies solely on a participant ID to authorize deletions, enabling attackers to remove other users (including poll owners) from polls. This impacts the integrity and availability of poll participation data. This issue has been patched in version 4.5.4.

## References
- https://github.com/lukevella/rallly/releases/tag/v4.5.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/65xxx/CVE-2025-65029.json
- https://github.com/lukevella/rallly/security/advisories/GHSA-f8jc-6746-ww95
- https://nvd.nist.gov/vuln/detail/CVE-2025-65029
