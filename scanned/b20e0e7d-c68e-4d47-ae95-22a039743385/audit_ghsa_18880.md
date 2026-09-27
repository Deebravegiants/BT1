# [H] thread-amount Vulnerable to Resource Exhaustion (Memory and Handle Leaks) on Windows and macOS

## Summary
Severity: High
Advisory: GHSA-jf9p-2fv9-2jp2
CVE: CVE-2025-65947
CWE: CWE-400, CWE-772
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-11-21
Source: https://github.com/advisories/GHSA-jf9p-2fv9-2jp2
Type: github-advisory

## Affected
- crates.io: `thread-amount` — affected >=0 <0.2.2

## Details
Affected versions of this crate contain resource leaks when querying thread counts on Windows and Apple platforms.

### Windows
The `thread_amount` function calls `CreateToolhelp32Snapshot` but fails to close the returned `HANDLE` using `CloseHandle`. Repeated calls to this function will cause the handle count of the process to grow indefinitely, eventually leading to system instability or process termination when the handle limit is reached.

### macOS / iOS
The `thread_amount` function calls `task_threads` (via Mach kernel APIs) which allocates memory for the thread list. The function fails to deallocate this memory using `vm_deallocate`. Repeated calls will result in a steady memory leak, eventually causing the process to be killed by the OOM (Out of Memory) killer.

### Impact
Long-running applications (such as servers, daemons, or monitoring tools) that use this crate to periodically check thread counts will eventually crash due to resource exhaustion.

### Resources

- https://github.com/jzeuzs/thread-amount/pull/29

## References
- https://github.com/jzeuzs/thread-amount/security/advisories/GHSA-jf9p-2fv9-2jp2
- https://nvd.nist.gov/vuln/detail/CVE-2025-65947
- https://github.com/jzeuzs/thread-amount/pull/29
- https://github.com/jzeuzs/thread-amount/commit/28860d4a38286609cb884c13b5b7941edc2390e5
- https://github.com/jzeuzs/thread-amount
- https://rustsec.org/advisories/RUSTSEC-2025-0125.html
