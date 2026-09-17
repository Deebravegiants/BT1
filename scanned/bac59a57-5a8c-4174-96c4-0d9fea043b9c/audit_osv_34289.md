# [H] CVE-2025-57616

## Summary
Severity: High
Advisory: CVE-2025-57616
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57616
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) A use-after-free vulnerability in the write_interleaved method allows an attacker to cause a denial of service or memory corruption. The method violates Rust's aliasing rules by modifying a data structure through a mutable pointer while only holding an immutable reference, which can lead to undefined behavior when the data is accessed later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57616.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57616
- https://github.com/meh/rust-ffmpeg/issues/192
