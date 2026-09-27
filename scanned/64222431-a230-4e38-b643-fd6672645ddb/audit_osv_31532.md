# [M] Libopensc: opensc: multiple uses of uninitialized variable

## Summary
Severity: Medium
Advisory: CVE-2025-13763
Aliases: GHSA-2v44-fq35-98vv
CVSS: 5.7 (CVSS:3.1/AV:P/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-23
Source: https://osv.dev/vulnerability/CVE-2025-13763
Type: osv

## Details
Multiple uses of uninitialized variables were found in libopensc that may lead to information disclosure or application crash. An attack requires a crafted USB device or smart card that would present the system with specially crafted responses to the APDUs

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://github.com/OpenSC/OpenSC/wiki/CVE-2025-13763
- https://access.redhat.com/security/cve/CVE-2025-13763
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/13xxx/CVE-2025-13763.json
- https://github.com/OpenSC/OpenSC/security/advisories/GHSA-2v44-fq35-98vv
- https://nvd.nist.gov/vuln/detail/CVE-2025-13763
- https://bugzilla.redhat.com/show_bug.cgi?id=2417581
