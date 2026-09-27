# [M] CVE-2024-22365

## Summary
Severity: Medium
Advisory: CVE-2024-22365
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-06
Source: https://osv.dev/vulnerability/CVE-2024-22365
Type: osv

## Details
linux-pam (aka Linux PAM) before 1.6.0 allows attackers to cause a denial of service (blocked login process) via mkfifo because the openat call (for protect_dir) lacks O_DIRECTORY.

## References
- http://www.openwall.com/lists/oss-security/2024/01/18/3
- https://cert-portal.siemens.com/productcert/html/ssa-577017.html
- https://cert-portal.siemens.com/productcert/html/ssa-794697.html
- https://github.com/linux-pam/linux-pam/releases/tag/v1.6.0
- https://lists.debian.org/debian-lts-announce/2025/09/msg00021.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/22xxx/CVE-2024-22365.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-22365
- https://github.com/linux-pam/linux-pam/commit/031bb5a5d0d950253b68138b498dc93be69a64cb
- https://github.com/linux-pam/linux-pam
