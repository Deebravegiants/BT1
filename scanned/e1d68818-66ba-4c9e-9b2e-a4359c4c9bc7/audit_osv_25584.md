# [H] Uncaught fastcdr exception (Unexpected CDR type received) crashing fastdds

## Summary
Severity: High
Advisory: CVE-2023-39948
Aliases: GHSA-x9pj-vrgf-f68f
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-08-11
Source: https://osv.dev/vulnerability/CVE-2023-39948
Type: osv

## Details
eprosima Fast DDS is a C++ implementation of the Data Distribution Service standard of the Object Management Group. Prior to versions 2.10.0 and 2.6.5, the `BadParamException` thrown by Fast CDR is not caught in Fast DDS. This can remotely crash any Fast DDS process. Versions 2.10.0 and 2.6.5 contain a patch for this issue.

## References
- https://github.com/eProsima/Fast-DDS/files/11117197/fastdds-assert.pcap.zip
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/39xxx/CVE-2023-39948.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-x9pj-vrgf-f68f
- https://nvd.nist.gov/vuln/detail/CVE-2023-39948
- https://www.debian.org/security/2023/dsa-5481
- https://github.com/eProsima/Fast-DDS/issues/3422
