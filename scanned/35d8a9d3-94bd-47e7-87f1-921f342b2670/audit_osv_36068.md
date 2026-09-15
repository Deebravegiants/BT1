# [H] Packer vulnerable to arbitrary file write via crafted plugin archive during installation

## Summary
Severity: High
Advisory: CVE-2026-19589
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-19589
Type: osv

## Details
Packer up to 1.15.4 is vulnerable to an issue in the third-party plugin installer that may allow unintended file system modification and could lead to code execution. A user who installs a plugin from a malicious or compromised source may be affected. This vulnerability (CVE-2026-19589) is fixed in Packer 1.16.0.

## References
- https://discuss.hashicorp.com/t/hcsec-2026-29-packer-vulnerable-to-arbitrary-file-write-via-crafted-plugin-archive-during-installation/77654
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19589.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19589
- https://github.com/hashicorp/packer
