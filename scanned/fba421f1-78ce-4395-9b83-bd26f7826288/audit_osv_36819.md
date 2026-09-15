# [H] OpenEMR Missing Authorization Checks in DICOM Viewer State API

## Summary
Severity: High
Advisory: CVE-2026-25927
Aliases: GHSA-qj9f-x7v2-hrr7
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2026-25927
Type: osv

## Details
OpenEMR is a free and open source electronic health records and medical practice management application. Prior to version 8.0.0,  the DICOM viewer state API (e.g. upload or state save/load) accepts a document ID (`doc_id`) without verifying that the document belongs to the current user’s authorized patient or encounter. An authenticated user can read or modify DICOM viewer state (e.g. annotations, view settings) for any document by enumerating document IDs. Version 8.0.0 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25927.json
- https://github.com/openemr/openemr/security/advisories/GHSA-qj9f-x7v2-hrr7
- https://nvd.nist.gov/vuln/detail/CVE-2026-25927
