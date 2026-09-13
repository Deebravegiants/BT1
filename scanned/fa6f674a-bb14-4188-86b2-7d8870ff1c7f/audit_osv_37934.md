# [M] OpenEMR has IDOR in Portal Payment Page that Allows Cross-Patient Record Access

## Summary
Severity: Medium
Advisory: CVE-2026-33931
Aliases: GHSA-hf37-5rp9-j27j
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-03-25
Source: https://osv.dev/vulnerability/CVE-2026-33931
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0.3, an Insecure Direct Object Reference (IDOR) vulnerability in the patient portal payment page allows any authenticated portal patient to access other patients' payment records — including invoice/billing data (PHI) and payment card metadata — by manipulating the `recid` query parameter in `portal/portal_payment.php`. Version 8.0.0.3 patches the issue.

## References
- https://github.com/openemr/openemr/releases/tag/v8_0_0_3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33931.json
- https://github.com/openemr/openemr/security/advisories/GHSA-hf37-5rp9-j27j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33931
- https://github.com/openemr/openemr/commit/7bf30e0ec5587f80c19094d58df09d46ac328806
