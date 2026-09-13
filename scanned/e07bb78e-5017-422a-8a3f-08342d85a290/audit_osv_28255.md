# [H] FastDDS heap buffer overflow when publisher sends malformed packet

## Summary
Severity: High
Advisory: CVE-2024-30259
Aliases: GHSA-qcj9-939p-p662
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-30259
Type: osv

## Details
FastDDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Prior to versions 2.14.1, 2.13.5, 2.10.4, and 2.6.8, when a publisher serves malformed `RTPS` packet, heap buffer overflow occurs on the subscriber. This can remotely crash any Fast-DDS process, potentially leading to a DOS attack. Versions 2.14.1, 2.13.5, 2.10.4, and 2.6.8 contain a patch for the issue.

## References
- https://drive.google.com/file/d/1Y2bGvP3UIOJCLh_XEURLdhrM2Sznlvlp/view?usp=sharing
- https://vimeo.com/907641887?share=copy
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30259.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-qcj9-939p-p662
- https://nvd.nist.gov/vuln/detail/CVE-2024-30259
