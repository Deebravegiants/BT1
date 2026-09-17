# [H] CVE-2025-57612

## Summary
Severity: High
Advisory: CVE-2025-57612
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-02
Source: https://osv.dev/vulnerability/CVE-2025-57612
Type: osv

## Details
An issue was discovered in rust-ffmpeg 0.3.0 (after comit 5ac0527) Null pointer dereference vulnerability in the name() method allows an attacker to cause a denial of service. The vulnerability exists because the method fails to check for a NULL return value from the av_get_sample_fmt_name() C function, which can be triggered by providing an unrecognized sample format.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/57xxx/CVE-2025-57612.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-57612
- https://github.com/meh/rust-ffmpeg/issues/192
