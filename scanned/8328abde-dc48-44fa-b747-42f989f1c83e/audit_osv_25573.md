# [H] Malformed GAP submessage triggers assertion failure

## Summary
Severity: High
Advisory: CVE-2023-39534
Aliases: GHSA-fcr6-x23w-94wp
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2023-39534
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.10.0, 2.9.2, and 2.6.5, a malformed GAP submessage can trigger assertion failure, crashing FastDDS. Version 2.10.0, 2.9.2, and 2.6.5 contain a patch for this issue.

## References
- https://bombshell.gtisc.gatech.edu/ddsfuzz/pcap/fastdds-assert-230509.pcap
- https://github.com/eProsima/Fast-DDS/blob/v2.9.1/include/fastdds/rtps/common/SequenceNumber.h#L238-L252
- https://github.com/eProsima/Fast-DDS/blob/v2.9.1/src/cpp/rtps/reader/StatefulReader.cpp#L863
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39534.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-fcr6-x23w-94wp
- https://nvd.nist.gov/vuln/detail/CVE-2023-39534
- https://www.debian.org/security/2023/dsa-5481
