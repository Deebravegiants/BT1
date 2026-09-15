# [M] CVE-2025-57611

## Summary
Severity: Medium
Advisory: CVE-2025-57611
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57611
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) Null pointer dereference vulnerability in the dump() method allows an attacker to cause a denial of service. The vulnerability exists because the method fails to check the return value of avfilter_graph_dump() for NULL, leading to a crash if the underlying memory allocation fails.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57611.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57611
- https://github.com/meh/rust-ffmpeg/issues/192
