# [H] FastDDS crash when publisher send malformed packet

## Summary
Severity: High
Advisory: CVE-2024-30258
Aliases: GHSA-53xw-465j-rxfh
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-13
Source: https://osv.dev/vulnerability/CVE-2024-30258
Type: osv

## Details
FastDDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group). Prior to versions 2.14.1, 2.13.5, 2.10.4, and 2.6.8, when a publisher serves a malformed `RTPS` packet, the subscriber crashes when creating `pthread`. This can remotely crash any Fast-DDS process, potentially leading to a DOS attack. Versions 2.14.1, 2.13.5, 2.10.4, and 2.6.8 contain a patch for the issue.

## References
- https://drive.google.com/file/d/19W5UC52hPnAqVq_boZWO45d1TJ4WoCSh/view?usp=sharing
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/30xxx/CVE-2024-30258.json
- https://github.com/eProsima/Fast-DDS/security/advisories/GHSA-53xw-465j-rxfh
- https://nvd.nist.gov/vuln/detail/CVE-2024-30258
- https://github.com/eProsima/Fast-DDS/commit/65236f93e9c4ea3ff9a49fba4dfd9e43eb94037b
