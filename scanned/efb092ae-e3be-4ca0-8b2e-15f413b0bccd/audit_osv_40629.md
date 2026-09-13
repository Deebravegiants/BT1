# [M] Capgo < 12.128.2 - Denial of Service via Unverified Email Account Registration and Deletion

## Summary
Severity: Medium
Advisory: CVE-2026-53868
Aliases: GHSA-3wfv-m8fq-7r5g
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-12
Source: https://osv.dev/vulnerability/CVE-2026-53868
Type: osv

## Details
Capgo before 12.128.2 contains a denial of service vulnerability allowing attackers to register accounts using arbitrary email addresses without verification, then initiate deletion to lock emails in pending deletion state. Attackers can permanently lock legitimate users out of the platform for 30 days by exploiting unverified email ownership in account lifecycle operations.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53868.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-3wfv-m8fq-7r5g
- https://nvd.nist.gov/vuln/detail/CVE-2026-53868
- https://www.vulncheck.com/advisories/capgo-denial-of-service-via-unverified-email-account-registration-and-deletion
- https://github.com/Cap-go/capgo
