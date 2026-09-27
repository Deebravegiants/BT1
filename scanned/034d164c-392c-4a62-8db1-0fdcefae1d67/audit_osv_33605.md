# [M] CVE-2025-47268

## Summary
Severity: Medium
Advisory: CVE-2025-47268
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-05-05
Source: https://osv.dev/vulnerability/CVE-2025-47268
Type: osv

## Details
ping in iputils before 20250602 allows a denial of service (application error or incorrect data collection) via a crafted ICMP Echo Reply packet, because of a signed 64-bit integer overflow in timestamp multiplication.

## References
- https://github.com/Zephkek/ping-rtt-overflow/
- https://github.com/iputils/iputils/releases/tag/20250602
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47268.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-47268
- https://bugzilla.suse.com/show_bug.cgi?id=1242300
- https://github.com/iputils/iputils/issues/584
- https://github.com/iputils/iputils/commit/070cfacd7348386173231fb16fad4983d4e6ae40
- https://github.com/iputils/iputils/pull/585
