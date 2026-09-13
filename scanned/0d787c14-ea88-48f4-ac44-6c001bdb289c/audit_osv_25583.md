# [H] Another heap overflow in push_back_helper

## Summary
Severity: High
Advisory: CVE-2023-39947
Aliases: GHSA-mf55-5747-c4pv
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2023-39947
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.11.1, 2.10.2, 2.9.2, and 2.6.6, even after the fix at commit 3492270, malformed `PID_PROPERTY_LIST` parameters cause heap overflow at a different program counter. This can remotely crash any Fast-DDS process. Versions 2.11.1, 2.10.2, 2.9.2, and 2.6.6 contain a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39947.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-mf55-5747-c4pv
- https://nvd.nist.gov/vuln/detail/CVE-2023-39947
- https://www.debian.org/security/2023/dsa-5481
- https://github.com/eProsima/Fast-DDS/commit/349227005827e8a67a0406b823138b5068cc47dc
