# [M] JavaScript Injection via url encoded values in links in Collabora Office Android

## Summary
Severity: Medium
Advisory: CVE-2024-45045
Aliases: GHSA-78cg-rg4q-26qv
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:L)
Published: 2024-08-29
Source: https://osv.dev/vulnerability/CVE-2024-45045
Type: osv

## Details
Collabora Online is a collaborative online office suite based on LibreOffice technology. In the mobile (Android/iOS) device variants of Collabora Online it was possible to inject JavaScript via url encoded values in links contained in documents. Since the Android JavaScript interface allows access to internal functions, the likelihood that the app could be compromised via this vulnerability is considered high. Non-mobile variants are not affected. Mobile variants should update to the latest version provided by the platform appstore. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45045.json
- https://github.com/CollaboraOnline/online/security/advisories/GHSA-78cg-rg4q-26qv
- https://nvd.nist.gov/vuln/detail/CVE-2024-45045
