# [M] Memory handling vulnerability in ProtocolBuffers Java core and lite

## Summary
Severity: Medium
Advisory: CVE-2022-3171
Aliases: GHSA-h4h5-3hr4-j3g2
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-10-12
Source: https://osv.dev/vulnerability/CVE-2022-3171
Type: osv

## Details
A parsing issue with binary data in protobuf-java core and lite versions prior to 3.21.7, 3.20.3, 3.19.6 and 3.16.3 can lead to a denial of service attack. Inputs containing multiple instances of non-repeated embedded messages with repeated or unknown fields causes objects to be converted back-n-forth between mutable and immutable forms, resulting in potentially long garbage collection pauses. We recommend updating to the versions mentioned above.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3171.json
- https://github.com/protocolbuffers/protobuf/security/advisories/GHSA-h4h5-3hr4-j3g2
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CBAUKJQL6O4TIWYBENORSY5P43TVB4M3/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MPCGUT3T5L6C3IDWUPSUO22QDCGQKTOP/
- https://nvd.nist.gov/vuln/detail/CVE-2022-3171
- https://security.gentoo.org/glsa/202301-09
