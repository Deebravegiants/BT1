# [H] Malformed DATA submessage leads to bad-free error in Fast-DDS

## Summary
Severity: High
Advisory: CVE-2023-42459
Aliases: GHSA-gq8g-fj58-22gm
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2023-10-16
Source: https://osv.dev/vulnerability/CVE-2023-42459
Type: osv

## Details
Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). In affected versions specific DATA submessages can be sent to a discovery locator which may trigger a free error. This can remotely crash any Fast-DDS process. The call to free() could potentially leave the pointer in the attackers control which could lead to a double free. This issue has been addressed in versions 2.12.0, 2.11.3, 2.10.3, and 2.6.7. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42459.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-gq8g-fj58-22gm
- https://nvd.nist.gov/vuln/detail/CVE-2023-42459
- https://www.debian.org/security/2023/dsa-5568
- https://github.com/eProsima/Fast-DDS/issues/3207
- https://github.com/eProsima/Fast-DDS/pull/3824
