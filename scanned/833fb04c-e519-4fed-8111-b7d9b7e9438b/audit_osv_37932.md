# [H] OpenEMR Missing Authorization on Claim File Download Endpoint

## Summary
Severity: High
Advisory: CVE-2026-33918
Aliases: GHSA-g3p5-5grq-m65m
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:L)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33918
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, the billing file-download endpoint `interface/billing/get_claim_file.php` only verifies that the caller has a valid session and CSRF token, but does not check any ACL permissions. This allows any authenticated OpenEMR user — regardless of whether they have billing privileges — to download and permanently delete electronic claim batch files containing protected health information (PHI). Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33918.json
- https://github.com/openemr/openemr/security/advisories/GHSA-g3p5-5grq-m65m
- https://nvd.nist.gov/vuln/detail/CVE-2026-33918
- https://github.com/openemr/openemr/commit/f6d98d0102df0a8f131be560d9208fb65fba6188
