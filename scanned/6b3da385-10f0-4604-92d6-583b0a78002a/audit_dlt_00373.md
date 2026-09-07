# [?] fix(testsuite): update Python dependencies to resolve security vulnerabilities (#18844)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2026-02-25
Source: https://github.com/aptos-labs/aptos-core/commit/3b523adba8ffffe33781bdac30647958342003b1
Type: security-commit

## Details
fix(testsuite): update Python dependencies to resolve security vulnerabilities (#18844)

Update poetry.lock files for both testsuite/ and testsuite/replay-verify/
to address the following CVEs:

- certifi: CVE-2024-39689 (GLOBALTRUST root cert) - updated to 2026.1.4
- urllib3: CVE-2023-43804, CVE-2023-45803, CVE-2024-37891, CVE-2025-66471,
  CVE-2026-21441 (decompression bombs, header/body leakage) - updated to 2.6.3
- requests: CVE-2024-35195, CVE-2024-47081 (TLS bypass, netrc leak) - updated to 2.32.5
- setuptools: CVE-2024-6345, CVE-2025-47273 (RCE, path traversal) - updated to 82.0.0

Also bumps minimum Python version from 3.8 to 3.9 in testsuite/pyproject.toml
since the secure versions of urllib3 (>=2.6.0) and setuptools (>=78.1.1)
require Python >=3.9.

Co-authored-by: Cursor Agent <cursoragent@cursor.com>
