# [M] tar-rs 0.4.11 - 0.4.46 Symlink Escape via append_dir_all()

## Summary
Severity: Medium
Advisory: CVE-2026-70622
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-70622
Type: osv

## Details
tar-rs versions 0.4.11 through 0.4.46 contain a symlink escape vulnerability in the Builder::append_dir_all() function that allows attackers to read files outside the intended source root directory by planting symlinks in an attacker-controlled directory. When a privileged process archives an untrusted directory, the function follows symlinks without verifying that resolved targets remain within the source root, causing out-of-bounds files to be included in the archive as regular files and disclosed to the attacker.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70622.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-70622
- https://www.vulncheck.com/advisories/tar-rs-symlink-escape-via-append-dir-all
- https://github.com/composefs/tar-rs
- https://gist.github.com/thesmartshadow/e7dac0bb690ee17b9cc142154cb11726
