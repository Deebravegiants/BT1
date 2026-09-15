# [C] Taskosaur Improper Role Assignment via Parameter Manipulation in User Registration

## Summary
Severity: Critical
Advisory: CVE-2026-31874
Aliases: GHSA-r6gj-4663-p5mr
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-03-11
Source: https://osv.dev/vulnerability/CVE-2026-31874
Type: osv

## Details
Taskosaur is an open source project management platform with conversational AI for task execution in-app. In 1.0.0, the application does not properly validate or restrict the role parameter during the user registration process. An attacker can manually modify the request payload and assign themselves elevated privileges. Because the backend does not enforce role assignment restrictions or ignore client-supplied role parameters, the server accepts the manipulated value and creates the account with SUPER_ADMIN privileges. This allows any unauthenticated attacker to register a fully privileged administrative account.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31874.json
- https://github.com/Taskosaur/Taskosaur/security/advisories/GHSA-r6gj-4663-p5mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-31874
- https://github.com/Taskosaur/Taskosaur/commit/159a5a8f43761561100a57d34309830550028932
