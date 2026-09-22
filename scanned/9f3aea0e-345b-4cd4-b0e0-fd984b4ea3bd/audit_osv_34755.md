# [M] Open Forms prefill data in read-only components can be tampered

## Summary
Severity: Medium
Advisory: CVE-2025-64515
Aliases: GHSA-cp63-63mq-5wvf
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-64515
Type: osv

## Details
Open Forms allows users create and publish smart forms. Prior to versions 3.2.7 and 3.3.3, forms where the prefill data fields are dynamically set to readonly/disabled can be modified by malicious users deliberately trying to modify data they're not supposed to. For regular users, the form fields are marked as readonly and cannot be modified through the user interface. This issue has been patched in versions 3.2.7 and 3.3.3.

## References
- https://github.com/open-formulieren/open-forms/blob/bcf2dc54c695fb7c8c58712627d82c4b766248b6/CHANGELOG.rst#327-2025-11-18
- https://github.com/open-formulieren/open-forms/blob/bcf2dc54c695fb7c8c58712627d82c4b766248b6/CHANGELOG.rst#333-2025-11-18
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64515.json
- https://github.com/open-formulieren/open-forms/security/advisories/GHSA-cp63-63mq-5wvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-64515
