# [M] In eLabFTW, if administrators can create users, users can too

## Summary
Severity: Medium
Advisory: CVE-2024-25633
Aliases: GHSA-v677-8x8p-636v
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2024-08-15
Source: https://osv.dev/vulnerability/CVE-2024-25633
Type: osv

## Details
eLabFTW is an open source electronic lab notebook for research labs. In an eLabFTW system, one can configure who is allowed to create new user accounts. A vulnerability has been found starting in version 4.4.0 and prior to version 5.0.0 that allows regular users to create new, validated accounts in their team. If the system has anonymous access enabled (disabled by default) an unauthenticated user can create regular users in any team. This vulnerability has been fixed since version 5.0.0, released on February 17th 2024. Some workarounds are available. Disabling both options that allow *administrators* to create users will provide a mitigation. Additionally, disabling anonymous user access will stop anonymous access (including using existing access keys).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/25xxx/CVE-2024-25633.json
- https://github.com/elabftw/elabftw/security/advisories/GHSA-v677-8x8p-636v
- https://nvd.nist.gov/vuln/detail/CVE-2024-25633
