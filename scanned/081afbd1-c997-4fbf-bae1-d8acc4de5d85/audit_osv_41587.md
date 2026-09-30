# [H] FlashAttention Symlink Attack via tarfile.extractall in hopper/setup.py

## Summary
Severity: High
Advisory: CVE-2026-62239
CVSS: 7.5 (CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-62239
Type: osv

## Details
FlashAttention through 2.8.3.post1, fixed in commit 0816ef1, contains a symlink attack vulnerability in the download_and_copy() function within hopper/setup.py that extracts NVIDIA toolchain archives without validating symlinks or filtering tar members. A local attacker can pre-plant a symlink in the predictable cache directory to redirect extracted binaries to an attacker-chosen location, enabling arbitrary file write with victim privileges during build time.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/62xxx/CVE-2026-62239.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-62239
- https://www.vulncheck.com/advisories/flashattention-symlink-attack-via-tarfile-extractall-in-hopper-setup-py
- https://github.com/Dao-AILab/flash-attention/issues/2637
- https://github.com/Dao-AILab/flash-attention/commit/0816ef12f424c6ec94b057a72c275b14f6e6edb2
- https://github.com/Dao-AILab/flash-attention/pull/2702
- https://github.com/Dao-AILab/flash-attention
