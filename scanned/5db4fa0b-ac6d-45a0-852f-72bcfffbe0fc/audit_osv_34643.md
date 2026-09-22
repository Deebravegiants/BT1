# [C] FastDDS's heap buffer overflow in RTPS DATA_FRAG enables unauthenticated DoS (potential RCE)

## Summary
Severity: Critical
Advisory: CVE-2025-62799
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-03
Source: https://osv.dev/vulnerability/CVE-2025-62799
Type: osv

## Details
Fast DDS is a C++ implementation of the DDS (Data Distribution Service) standard of the OMG (Object Management Group
). Prior to versions 3.4.1, 3.3.1, and 2.6.11, a heap buffer overflow exists in the Fast-DDS DATA_FRAG receive path. An un
authenticated sender can transmit a single malformed RTPS DATA_FRAG packet where `fragmentSize` and `sampleSize` are craft
ed to violate internal assumptions. Due to a 4-byte alignment step during fragment metadata initialization, the code write
s past the end of the allocated payload buffer, causing immediate crash (DoS) and potentially enabling memory corruption (
RCE risk). Versions 3.4.1, 3.3.1, and 2.6.11 patch the issue.

## References
- https://security-tracker.debian.org/tracker/CVE-2025-62799
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/62xxx/CVE-2025-62799.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-62799
- https://github.com/eProsima/Fast-DDS/commit/0c3824ef4991628de5dfba240669dc6172d63b46
- https://github.com/eProsima/Fast-DDS/commit/955c8a15899dc6eb409e080fe7dc89e142d5a514
- https://github.com/eProsima/Fast-DDS/commit/d6dd58f4ecd28cd1c3bc4ef0467be9110fa94659
- https://github.com/eProsima/Fast-DDS
