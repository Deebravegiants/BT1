# [H] Out of Memory issue in ProtocolBuffers for cpp and python

## Summary
Severity: High
Advisory: CVE-2022-1941
Aliases: GHSA-8gq9-2x98-w8hf, PYSEC-2026-899
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-22
Source: https://osv.dev/vulnerability/CVE-2022-1941
Type: osv

## Details
A parsing vulnerability for the MessageSet type in the ProtocolBuffers versions prior to and including 3.16.1, 3.17.3, 3.18.2, 3.19.4, 3.20.1 and 3.21.5 for protobuf-cpp, and versions prior to and including 3.16.1, 3.17.3, 3.18.2, 3.19.4, 3.20.1 and 4.21.5 for protobuf-python can lead to out of memory failures. A specially crafted message with multiple key-value per elements creates parsing issues, and can lead to a Denial of Service against services receiving unsanitized input. We recommend upgrading to versions 3.18.3, 3.19.5, 3.20.2, 3.21.6 for protobuf-cpp and 3.18.3, 3.19.5, 3.20.2, 4.21.6 for protobuf-python. Versions for 3.16 and 3.17 are no longer updated.

## References
- https://cloud.google.com/support/bulletins#GCP-2022-019
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/1xxx/CVE-2022-1941.json
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-8gq9-2x98-w8hf
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBAUKJQL6O4TIWYBENORSY5P43TVB4M3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MPCGUT3T5L6C3IDWUPSUO22QDCGQKTOP/
- https://nvd.nist.gov/vuln/detail/CVE-2022-1941
- https://security.netapp.com/advisory/ntap-20240705-0001/
- http://www.openwall.com/lists/oss-security/2022/09/27/1
- https://lists.debian.org/debian-lts-announce/2023/04/msg00019.html
