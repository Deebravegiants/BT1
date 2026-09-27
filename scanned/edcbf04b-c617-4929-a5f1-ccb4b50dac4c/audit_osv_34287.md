# [H] CVE-2025-57614

## Summary
Severity: High
Advisory: CVE-2025-57614
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57614
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) Integer overflow and invalid input vulnerability in the cached method allows an attacker to cause a denial of service or potentially execute arbitrary code. The vulnerability occurs when dimension parameters are zero or exceed i32::MAX, leading to an unchecked cast that violates the underlying C function's preconditions and triggers undefined behavior.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57614.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57614
- https://github.com/meh/rust-ffmpeg/issues/192
