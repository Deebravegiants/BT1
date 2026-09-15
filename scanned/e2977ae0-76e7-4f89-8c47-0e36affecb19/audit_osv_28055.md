# [M] Content spoofing - real Hoppscotch emails

## Summary
Severity: Medium
Advisory: CVE-2024-27092
Aliases: GHSA-8r6h-8r68-q3pp
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-02-26
Source: https://osv.dev/vulnerability/CVE-2024-27092
Type: osv

## Details
Hoppscotch is an API development ecosystem.  Due to lack of validation for fields like Label (Edit Team) - TeamName, bad actors can send emails with Spoofed Content as Hoppscotch. Part of payload (external link) is presented in clickable form - easier to achieve own goals by malicious actors.  This issue is fixed in 2023.12.6.

## References
- https://github.com/hoppscotch/hoppscotch/blob/main/packages/hoppscotch-backend/src/team-invitation/team-invitation.service.ts#L153
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27092.json
- https://github.com/hoppscotch/hoppscotch/security/advisories/GHSA-8r6h-8r68-q3pp
- https://nvd.nist.gov/vuln/detail/CVE-2024-27092
- https://github.com/hoppscotch/hoppscotch/commit/6827e97ec583b2534cdc1c2f33fa44973a0c2bf5
