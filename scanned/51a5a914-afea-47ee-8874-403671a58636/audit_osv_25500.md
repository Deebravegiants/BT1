# [H] Malformed PID_PROPERTY_LIST parameter in DATA submessage remotely crashes OpenDDS

## Summary
Severity: High
Advisory: CVE-2023-37915
Aliases: GHSA-v5pp-7prc-5xq9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-07-21
Source: https://osv.dev/vulnerability/CVE-2023-37915
Type: osv

## Details
OpenDDS is an open source C++ implementation of the Object Management Group (OMG) Data Distribution Service (DDS). OpenDDS crashes while parsing a malformed `PID_PROPERTY_LIST` in a DATA submessage during participant discovery. Attackers can remotely crash OpenDDS processes by sending a DATA submessage containing the malformed parameter to the known multicast port. This issue has been addressed in version 3.25. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/OpenDDS/OpenDDS/releases/tag/DDS-3.25
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37915.json
- https://github.com/OpenDDS/OpenDDS/security/advisories/GHSA-v5pp-7prc-5xq9
- https://nvd.nist.gov/vuln/detail/CVE-2023-37915
