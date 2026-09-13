# [M] Specially crafted RTPS message may cause an OpenDDS application to crash

## Summary
Severity: Medium
Advisory: CVE-2023-23932
Aliases: GHSA-8wvq-25f5-f8h4
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2023-23932
Type: osv

## Details
OpenDDS is an open source C++ implementation of the Object Management Group (OMG) Data Distribution Service (DDS). OpenDDS applications that are exposed to untrusted RTPS network traffic may crash when parsing badly-formed input. This issue has been patched in version 3.23.1.

## References
- https://github.com/OpenDDS/OpenDDS/releases/tag/DDS-3.23.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23932.json
- https://github.com/OpenDDS/OpenDDS/security/advisories/GHSA-8wvq-25f5-f8h4
- https://nvd.nist.gov/vuln/detail/CVE-2023-23932
