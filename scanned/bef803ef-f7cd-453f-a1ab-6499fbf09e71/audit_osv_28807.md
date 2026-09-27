# [M] CVE-2024-36845

## Summary
Severity: Medium
Advisory: CVE-2024-36845
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-05-31
Source: https://osv.dev/vulnerability/CVE-2024-36845
Type: osv

## Details
An invalid pointer in the modbus_receive() function of libmodbus v3.1.6 allows attackers to cause a Denial of Service (DoS) via a crafted message sent to the unit-test-server.

## References
- https://lists.debian.org/debian-lts-announce/2025/03/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36845.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36845
- https://github.com/stephane/libmodbus/issues/750
