# [M] Titra API Contains Mass Assignment Vulnerability

## Summary
Severity: Medium
Advisory: CVE-2026-21695
Aliases: GHSA-gc65-vr47-jppq
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-01-07
Source: https://osv.dev/vulnerability/CVE-2026-21695
Type: osv

## Details
Titra is open source project time tracking software. In versions 0.99.49 and below, an API has a Mass Assignment vulnerability which allows authenticated users to inject arbitrary fields into time entries, bypassing business logic controls via the customfields parameter. The affected endpoint uses the JavaScript spread operator (...customfields) to merge user-controlled input directly into the database document. While customfields is validated as an Object type, there is no validation of which keys are permitted inside that object. This allows attackers to overwrite protected fields such as userId, hours, and state. The issue is fixed in version 0.99.50.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/21xxx/CVE-2026-21695.json
- https://github.com/kromitgmbh/titra/security/advisories/GHSA-gc65-vr47-jppq
- https://nvd.nist.gov/vuln/detail/CVE-2026-21695
- https://github.com/kromitgmbh/titra/commit/29e6b88eca005107729e45a6f1731cf0fa5f8938
