# [M] Wallos: Shared local webhook allowlist lets low-privilege users send arbitrary requests to allowlisted internal services

## Summary
Severity: Medium
Advisory: CVE-2026-41689
Aliases: GHSA-jx6w-832g-42wv
CVSS: 6.0 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-05-07
Source: https://osv.dev/vulnerability/CVE-2026-41689
Type: osv

## Details
Wallos is an open-source, self-hostable personal subscription tracker. In versions 4.8.4 and prior, the webhook notification feature reuses an administrator-configured local-target allowlist for every logged-in user. Any normal user can fully control a webhook URL, headers, and body, then use Wallos to send server-side requests to allowlisted internal automation services. When such a target exposes deployment or execution APIs, this can further enable adjacent-service RCE, but that downstream result is conditional on the target service. At time of publication, there are no publicly available patches.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41689.json
- https://github.com/ellite/Wallos/security/advisories/GHSA-jx6w-832g-42wv
- https://nvd.nist.gov/vuln/detail/CVE-2026-41689
