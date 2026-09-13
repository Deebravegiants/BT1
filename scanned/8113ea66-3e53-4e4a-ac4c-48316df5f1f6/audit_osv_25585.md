# [H] Improper validation of sequence numbers leading to remotely reachable assertion failure

## Summary
Severity: High
Advisory: CVE-2023-39949
Aliases: GHSA-3jv9-j9x3-95cg
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2023-39949
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.9.1 and 2.6.5, improper validation of sequence numbers may lead to remotely reachable assertion failure. This can remotely crash any Fast-DDS process. Versions 2.9.1 and 2.6.5 contain a patch for this issue.

## References
- https://github.com/eProsima/Fast-DDS/blob/v2.9.0/src/cpp/rtps/messages/MessageReceiver.cpp#L1059
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39949.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-3jv9-j9x3-95cg
- https://nvd.nist.gov/vuln/detail/CVE-2023-39949
- https://www.debian.org/security/2023/dsa-5481
- https://github.com/eProsima/Fast-DDS/issues/3236
