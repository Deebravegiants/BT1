# [H] CVE-2024-37408

## Summary
Severity: High
Advisory: CVE-2024-37408
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-06-08
Source: https://osv.dev/vulnerability/CVE-2024-37408
Type: osv

## Details
fprintd through 1.94.3 lacks a security attention mechanism, and thus unexpected actions might be authorized by "auth sufficient pam_fprintd.so" for Sudo. NOTE: the supplier disputes this because they believe issue resolution would involve modifying the PAM configuration to restrict pam_fprintd.so to front-ends that implement a proper attention mechanism, not modifying pam_fprintd.so or fprintd.

## References
- https://gitlab.freedesktop.org/libfprint/fprintd/-/releases
- https://lists.freedesktop.org/archives/fprint/2024-May/001231.html
- https://www.openwall.com/lists/oss-security/2024/05/30/3
- https://www.openwall.com/lists/oss-security/2024/06/13/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/37xxx/CVE-2024-37408.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-37408
- http://www.openwall.com/lists/oss-security/2024/06/13/3
- http://www.openwall.com/lists/oss-security/2024/06/14/1
- http://www.openwall.com/lists/oss-security/2024/06/14/2
- http://www.openwall.com/lists/oss-security/2024/06/14/3
