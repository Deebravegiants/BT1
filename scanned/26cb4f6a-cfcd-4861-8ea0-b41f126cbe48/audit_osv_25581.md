# [H] Malformed serialized data in a data submessage leads to unhandled exception

## Summary
Severity: High
Advisory: CVE-2023-39945
Aliases: GHSA-2rq6-8j7x-frr9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2023-39945
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.11.0, 2.10.2, 2.9.2, and 2.6.5, a data submessage sent to PDP port raises unhandled `BadParamException` in fastcdr, which in turn crashes fastdds. Versions 2.11.0, 2.10.2, 2.9.2, and 2.6.5 contain a patch for this issue.

## References
- https://bombshell.gtisc.gatech.edu/ddsfuzz/pcap/fastdds-exception-20230509-02.pcap
- https://github.com/eProsima/Fast-CDR/blob/v1.0.26/src/cpp/Cdr.cpp#L72-L79
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39945.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-2rq6-8j7x-frr9
- https://nvd.nist.gov/vuln/detail/CVE-2023-39945
- https://www.debian.org/security/2023/dsa-5481
