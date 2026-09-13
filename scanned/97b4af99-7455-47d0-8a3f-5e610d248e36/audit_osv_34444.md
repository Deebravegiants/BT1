# [H] NanoMQ has Buffer Overflow

## Summary
Severity: High
Advisory: CVE-2025-59947
Aliases: GHSA-98f4-cmg8-x7f3
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:L/VI:H/VA:H/SC:L/SI:H/SA:H)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-59947
Type: osv

## Details
NanoMQ is a messaging broker/bus for IoT Edge & SDV. Versions prior to 0.24.4 have a buffer overflow case while the PUBLISH packets trigger both shared subscription and vanila subscription. This is fixed in version 0.24.4. As a workaround, disable shared subscription.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/59xxx/CVE-2025-59947.json
- https://github.com/nanomq/nanomq/security/advisories/GHSA-98f4-cmg8-x7f3
- https://nvd.nist.gov/vuln/detail/CVE-2025-59947
- https://github.com/nanomq/nanomq/issues/2110
- https://github.com/nanomq/nanomq/commit/5f5581054bb92f102cf99251e8af2f43763d457b
