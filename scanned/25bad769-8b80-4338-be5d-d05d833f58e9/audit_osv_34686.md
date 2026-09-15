# [M] CVE-2025-63829

## Summary
Severity: Medium
Advisory: CVE-2025-63829
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-11-18
Source: https://osv.dev/vulnerability/CVE-2025-63829
Type: osv

## Details
eProsima Fast-DDS v3.3 and before has an infinite loop vulnerability caused by integer overflow in the Time_t:: fraction() function.

## References
- https://gist.github.com/lkloliver/b00377bec754d4aa1dc731be210d5889
- https://github.com/eProsima/Fast-DDS/blob/master/src/cpp/fastdds/core/Time_t.cpp#L67
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/63xxx/CVE-2025-63829.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-63829
