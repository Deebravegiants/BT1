# [M] Capgo - Unauthorized Manifest Insertion via Read-Only Org Member

## Summary
Severity: Medium
Advisory: CVE-2026-56220
Aliases: GHSA-vmgg-crr8-887p
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-56220
Type: osv

## Details
Capgo before 12.128.2 contains an authorization bypass vulnerability in the public.manifest INSERT policy that allows read-only org members to insert OTA manifest rows. Attackers with read-only org access can inject malicious manifest entries with arbitrary s3_path values that are served to devices via the unauthenticated /updates endpoint, enabling OTA metadata poisoning and potential malicious asset delivery.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/56xxx/CVE-2026-56220.json
- https://github.com/Cap-go/capgo/security/advisories/GHSA-vmgg-crr8-887p
- https://nvd.nist.gov/vuln/detail/CVE-2026-56220
- https://www.vulncheck.com/advisories/capgo-unauthorized-manifest-insertion-via-read-only-org-member
