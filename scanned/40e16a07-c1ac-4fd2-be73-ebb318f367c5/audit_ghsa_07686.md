# [C] Unstructured has Path Traversal via Malicious MSG Attachment that Allows Arbitrary File Write

## Summary
Severity: Critical
Advisory: GHSA-gm8q-m8mv-jj5m
CVE: CVE-2025-64712
CWE: CWE-22, CWE-73
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-02-03
Source: https://github.com/advisories/GHSA-gm8q-m8mv-jj5m
Type: github-advisory

## Affected
- PyPI: `unstructured` — affected >=0 <0.18.18

## Details
A Path Traversal vulnerability in the `partition_msg` function allows an attacker to write or overwrite arbitrary files on the filesystem when processing malicious MSG files with attachments.

  ## Impact
  An attacker can craft a malicious .msg file with attachment filenames containing path traversal sequences (e.g.,
  `../../../etc/cron.d/malicious`). When processed with `process_attachments=True`, the library writes the attachment to an
  attacker-controlled path, potentially leading to:

  - Arbitrary file overwrite
  - Remote code execution (via overwriting configuration files, cron jobs, or Python packages)
  - Data corruption
  - Denial of service

  ## Affected Functionality
  The vulnerability affects the MSG file partitioning functionality when `process_attachments=True` is enabled.

  ## Vulnerability Details
  The library does not sanitize attachment filenames in MSG files before using them in file write operations, allowing directory
  traversal sequences to escape the intended output directory.

  ## Workarounds
  Until patched, users can:
  - Set `process_attachments=False` when processing untrusted MSG files
  - Avoid processing MSG files from untrusted sources
  - Implement additional filename validation before processing

## References
- https://github.com/Unstructured-IO/unstructured/security/advisories/GHSA-gm8q-m8mv-jj5m
- https://nvd.nist.gov/vuln/detail/CVE-2025-64712
- https://github.com/Unstructured-IO/unstructured/commit/b01d35b2373fd087d2e15162b9c021663c97155d
- https://github.com/Unstructured-IO/unstructured
