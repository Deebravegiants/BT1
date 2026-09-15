# [M] Trustee's attestation-policy endpoint is not protected by admin autentication

## Summary
Severity: Medium
Advisory: CVE-2025-61779
Aliases: GHSA-49mc-2q77-m99x
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2025-10-09
Source: https://osv.dev/vulnerability/CVE-2025-61779
Type: osv

## Details
Confidential Containers's Trustee project contains tools and components for attesting confidential guests and providing secrets to them. In versions prior to 0.15.0, the attestation-policy endpoint didn't check if the kbs-client submitting the request was actually authenticated (had the right key). This allowed any kbs-client to actually change the attestation policy. Version 0.15.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/61xxx/CVE-2025-61779.json
- https://github.com/confidential-containers/trustee/security/advisories/GHSA-49mc-2q77-m99x
- https://nvd.nist.gov/vuln/detail/CVE-2025-61779
- https://github.com/confidential-containers/trustee/commit/3a7d04a70918fa503a00974dcae653cf9f0640e0
- https://github.com/confidential-containers/trustee/pull/957
