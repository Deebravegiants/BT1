# [M] comm: FIFO/pipe inputs are drained before comparison (data loss / hang)

## Summary
Severity: Medium
Advisory: GHSA-3wfc-mgpm-9rq6
CVE: CVE-2026-35347
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-07-06
Source: https://github.com/advisories/GHSA-3wfc-mgpm-9rq6
Type: github-advisory

## Affected
- crates.io: `uu_comm` — affected >=0 <0.6.0

## Details
The comm utility in uutils coreutils incorrectly consumes data from non-regular file inputs before performing comparison operations. The are_files_identical function opens and reads from both input paths to compare content without first verifying if the paths refer to regular files. If an input path is a FIFO or a pipe, this pre-read operation drains the stream, leading to silent data loss before the actual comparison logic is executed. Additionally, the utility may hang indefinitely if it attempts to pre-read from infinite streams like /dev/zero.

---
_Zellic finding 3.35. Reported in the Zellic *uutils coreutils Program Security Assessment* (for Canonical, Jan 2026), audited commit `3a07ffc5a9bd4c283e75afa548ba1f1957bad242`._

## References
- https://github.com/uutils/coreutils/security/advisories/GHSA-3wfc-mgpm-9rq6
- https://nvd.nist.gov/vuln/detail/CVE-2026-35347
- https://github.com/uutils/coreutils/pull/9545
- https://github.com/uutils/coreutils/commit/75f45e87e52ed95840494963ab9a28651165d56e
- https://github.com/uutils/coreutils
- https://github.com/uutils/coreutils/releases/tag/0.6.0
