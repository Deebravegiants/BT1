# [M] SPDK is vulnerable to buffer overflow in the NVMe-oF target component

## Summary
Severity: Medium
Advisory: GHSA-5m5w-w2h2-fqgq
CVE: CVE-2025-57275
CWE: CWE-119, CWE-120
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-10-01
Source: https://github.com/advisories/GHSA-5m5w-w2h2-fqgq
Type: github-advisory

## Affected
- PyPI: `spdk` — affected >=0 <25.9

## Details
Storage Performance Development Kit (SPDK) 25.05 is vulnerable to Buffer Overflow in the NVMe-oF target component in SPDK - lib/nvmf.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57275
- https://github.com/spdk/spdk/commit/8981ddb1ccaf54f85d34482a5a644e075b58cb36
- https://github.com/spdk/spdk/commit/f786c6d75f5c5162363a621b24f5449c729679c9
- https://github.com/spdk/spdk
- https://spdk.io
