# [C] OpenEMR's payments gateway_api_key secret rendered into client JS code

## Summary
Severity: Critical
Advisory: CVE-2026-25146
Aliases: GHSA-2hq8-wc73-jvvq
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2026-03-03
Source: https://osv.dev/vulnerability/CVE-2026-25146
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. From 5.0.2 to before 8.0.0, there are (at least) two paths where the gateway_api_key secret value is rendered to the client in plaintext. These secret keys being leaked could result in arbitrary money movement or broad account takeover of payment gateway APIs. This vulnerability is fixed in 8.0.0.

## References
- https://github.com/openemr/openemr/blob/6a4e18c5ec73e0c755f6f65b28a9652aded1a58b/interface/patient_file/front_payment.php#L765
- https://github.com/openemr/openemr/blob/6a4e18c5ec73e0c755f6f65b28a9652aded1a58b/portal/portal_payment.php#L537
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25146.json
- https://github.com/openemr/openemr/security/advisories/GHSA-2hq8-wc73-jvvq
- https://nvd.nist.gov/vuln/detail/CVE-2026-25146
- https://github.com/openemr/openemr/commit/fe6341496dc82d5b4f5a3f35891bb2e2481f3b25
