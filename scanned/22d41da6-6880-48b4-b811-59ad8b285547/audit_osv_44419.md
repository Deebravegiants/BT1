# [M] SvelteKit 2.49.0 before 2.53.3 Denial of Service via form

## Summary
Severity: Medium
Advisory: CVE-2026-82259
Aliases: GHSA-fpg4-jhqr-589c
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-82259
Type: osv

## Details
SvelteKit versions from 2.49.0 through 2.53.2 (fixed in 2.53.3) contain a deserialization expansion issue in the experimental form remote function. When an application enables experimental.remoteFunctions and uses the form function to process the files array without validating files.length or individual file sizes, an attacker can submit relatively small inputs that expand into very large file arrays, leading to expensive processing and denial of service.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82259.json
- https://github.com/sveltejs/kit/security/advisories/GHSA-fpg4-jhqr-589c
- https://nvd.nist.gov/vuln/detail/CVE-2026-82259
- https://www.vulncheck.com/advisories/sveltekit-2.49.0-before-2.53.3-denial-of-service-via-form
