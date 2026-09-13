# [M] Integer Overflow in rxi/microtar mtar_next() Causes Infinite Loop DoS

## Summary
Severity: Medium
Advisory: CVE-2026-54417
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-54417
Type: osv

## Details
An integer overflow in the mtar_next function in src/microtar.c in rxi microtar 0.1.0 allows a remote attacker to cause a denial of service (uncontrolled CPU consumption / infinite loop) via a crafted tar archive. mtar_next computes the offset to the next record as round_up(h.size, 512) + sizeof(mtar_raw_header_t) using 32-bit arithmetic.

## References
- https://github.com/rxi/microtar/blob/master/src/microtar.c#L239
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54417.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-54417
- https://github.com/rxi/microtar
- https://raw.githubusercontent.com/rxi/microtar/master/src/microtar.c
