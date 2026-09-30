# [H] onnx allows Arbitrary File Overwrite in download_model_with_test_data

## Summary
Severity: High
Advisory: GHSA-6rq9-53c3-f7vj
CVE: CVE-2024-5187
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-06
Source: https://github.com/advisories/GHSA-6rq9-53c3-f7vj
Type: github-advisory

## Affected
- PyPI: `onnx` — affected >=0 <1.16.2

## Details
A vulnerability in the `download_model_with_test_data` function of the onnx/onnx framework, versions before 1.16.2, allow for arbitrary file overwrite due to inadequate prevention of path traversal attacks in malicious tar files. This vulnerability enables attackers to overwrite any file on the system, potentially leading to remote code execution, deletion of system, personal, or application files, thus impacting the integrity and availability of the system. The issue arises from the function's handling of tar file extraction without performing security checks on the paths within the tar file, as demonstrated by the ability to overwrite the `/home/kali/.ssh/authorized_keys` file by specifying an absolute path in the malicious tar file.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-5187
- https://github.com/onnx/onnx/issues/6215
- https://github.com/onnx/onnx/pull/6145
- https://github.com/onnx/onnx/pull/6222
- https://github.com/onnx/onnx/pull/6959
- https://github.com/onnx/onnx/pull/7040
- https://github.com/onnx/onnx/commit/1b70f9b673259360b6a2339c4bd97db9ea6e552f
- https://github.com/onnx/onnx/commit/3fc3845edb048df559aa2a839e39e95503a0ee34
- https://github.com/advisories/GHSA-6rq9-53c3-f7vj
- https://github.com/onnx/onnx
- https://github.com/onnx/onnx/releases/tag/v1.16.2
- https://github.com/pypa/advisory-database/tree/main/vulns/onnx/PYSEC-2025-148.yaml
- https://huntr.com/bounties/50235ebd-3410-4ada-b064-1a648e11237e
- https://www.gecko.security/blog/cve-2025-51480
