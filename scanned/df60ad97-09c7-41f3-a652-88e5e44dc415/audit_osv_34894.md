# [C] OpenObserve's Invite Token Lifecycle Misconfiguration

## Summary
Severity: Critical
Advisory: CVE-2025-66223
Aliases: GHSA-c856-2xpx-gw75
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-11-29
Source: https://osv.dev/vulnerability/CVE-2025-66223
Type: osv

## Details
OpenObserve is a cloud-native observability platform. Prior to version 0.16.0, organization invitation tokens do not expire once issued, remain valid even after the invited user is removed from the organization, and allow multiple invitations to the same email with different roles where all issued links remain valid simultaneously. This results in broken access control where a removed or demoted user can regain access or escalate privileges. This issue has been patched in version 0.16.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66223.json
- https://github.com/openobserve/openobserve/security/advisories/GHSA-c856-2xpx-gw75
- https://nvd.nist.gov/vuln/detail/CVE-2025-66223
