# [H] CVE-2025-57615

## Summary
Severity: High
Advisory: CVE-2025-57615
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57615
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) An integer overflow vulnerability in the Vector::new constructor function allows an attacker to cause a denial of service via a null pointer dereference. The vulnerability stems from an unchecked cast of a usize parameter to c_int, which can result in a negative value being passed to the underlying C function sws_allocVec().

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57615.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57615
- https://github.com/meh/rust-ffmpeg/issues/192
