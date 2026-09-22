# [H] Apache Arrow: Potential use-after-free when reading IPC file with pre-buffering

## Summary
Severity: High
Advisory: GHSA-rgxp-2hwp-jwgg
CVE: CVE-2026-25087
CWE: CWE-416
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-rgxp-2hwp-jwgg
Type: github-advisory

## Affected
- PyPI: `pyarrow` — affected >=15.0.0 <23.0.1

## Details
Use After Free vulnerability in Apache Arrow C++.

This issue affects Apache Arrow C++ from 15.0.0 through 23.0.0. It can be triggered when reading an Arrow IPC file (but not an IPC stream) with pre-buffering enabled, if the IPC file contains data with variadic buffers (such as Binary View and String View data). Depending on the number of variadic buffers in a record batch column and on the temporal sequence of multi-threaded IO, a write to a dangling pointer could occur. The value (a `std::shared_ptr<Buffer>` object) that is written to the dangling pointer is not under direct control of the attacker.

Pre-buffering is disabled by default but can be enabled using a specific C++ API call (`RecordBatchFileReader::PreBufferMetadata`). The functionality is not exposed in language bindings (Python, Ruby, C GLib), so these bindings are not vulnerable.

The most likely consequence of this issue would be random crashes or memory corruption when reading specific kinds of IPC files. If the application allows ingesting IPC files from untrusted sources, this could plausibly be exploited for denial of service. Inducing more targeted kinds of misbehavior (such as confidential data extraction from the running process) depends on memory allocation and multi-threaded IO temporal patterns that are unlikely to be easily controlled by an attacker.

Advice for users of Arrow C++:

1. check whether you enable pre-buffering on the IPC file reader (using `RecordBatchFileReader::PreBufferMetadata`)

2. if so, either disable pre-buffering (which may have adverse performance consequences), or switch to Arrow 23.0.1 which is not vulnerable

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-25087
- https://github.com/apache/arrow/pull/48925
- https://github.com/apache/arrow
- https://github.com/pypa/advisory-database/tree/main/vulns/pyarrow/PYSEC-2026-113.yaml
- https://lists.apache.org/thread/mpm4ld1qony30tchfpjtk5b11tcyvmwh
- http://www.openwall.com/lists/oss-security/2026/02/17/4
