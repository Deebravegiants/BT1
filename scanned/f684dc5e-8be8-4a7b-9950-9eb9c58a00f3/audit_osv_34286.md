# [H] CVE-2025-57613

## Summary
Severity: High
Advisory: CVE-2025-57613
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57613
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) A null pointer dereference vulnerability in the input() constructor function allows an attacker to cause a denial of service. The vulnerability is triggered when the avio_alloc_context() call fails and returns NULL, which is then stored and later dereferenced by the Io struct's Drop implementation.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57613.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57613
- https://github.com/meh/rust-ffmpeg/issues/192
