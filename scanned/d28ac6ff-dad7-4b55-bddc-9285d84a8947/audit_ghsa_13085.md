# [M] pimcore/customer-management-framework-bundle Cross-site Scripting vulnerability in Segment name

## Summary
Severity: Medium
Advisory: GHSA-735f-w79p-282x
CVE: CVE-2023-4145
CWE: CWE-79, CWE-87
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2023-08-03
Source: https://github.com/advisories/GHSA-735f-w79p-282x
Type: github-advisory

## Affected
- Packagist: `pimcore/customer-management-framework-bundle` — affected >=0 <3.4.2

## Details
### Impact
As HTML injection works in email an attacker can trick a victim to click on such hyperlinks to redirect him to any malicious site and also can host a XSS page. All this will surely cause some damage to the victim. This could lead to users being tricked into giving logins away to malicious attackers.

### Patches
Update to version 3.4.2 or apply this patch manually https://github.com/pimcore/customer-data-framework/commit/72f45dd537a706954e7a71c99fbe318640e846a2.patch

### Workarounds
Apply https://github.com/pimcore/customer-data-framework/commit/72f45dd537a706954e7a71c99fbe318640e846a2.patch manually.

### References
https://huntr.dev/bounties/ce852777-2994-40b4-bb4e-c4d10023eeb0/

## References
- https://github.com/pimcore/customer-data-framework/security/advisories/GHSA-735f-w79p-282x
- https://nvd.nist.gov/vuln/detail/CVE-2023-4145
- https://github.com/pimcore/customer-data-framework/commit/72f45dd537a706954e7a71c99fbe318640e846a2
- https://github.com/pimcore/customer-data-framework/commit/72f45dd537a706954e7a71c99fbe318640e846a2.patch
- https://github.com/pimcore/customer-data-framework
- https://huntr.dev/bounties/ce852777-2994-40b4-bb4e-c4d10023eeb0
