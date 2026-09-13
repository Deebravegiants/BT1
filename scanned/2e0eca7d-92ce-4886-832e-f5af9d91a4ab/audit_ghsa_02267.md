# [M] Race condition in tokio

## Summary
Severity: Medium
Advisory: GHSA-2grh-hm3w-w7hv
CVE: CVE-2021-38191
CWE: CWE-362, CWE-366
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-25
Source: https://github.com/advisories/GHSA-2grh-hm3w-w7hv
Type: github-advisory

## Affected
- crates.io: `tokio` — affected >=1.8.0 <1.8.1
- crates.io: `tokio` — affected >=1.7.0 <1.7.2
- crates.io: `tokio` — affected >=1.6.0 <1.6.3
- crates.io: `tokio` — affected >=0.3.0 <1.5.1

## Details
When aborting a task with JoinHandle::abort, the future is dropped in the thread calling abort if the task is not currently being executed. This is incorrect for tasks spawned on a LocalSet. This can easily result in race conditions as many projects use Rc or RefCell in their Tokio tasks for better performance.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-38191
- https://github.com/tokio-rs/tokio/issues/3929
- https://github.com/tokio-rs/tokio
- https://raw.githubusercontent.com/rustsec/advisory-db/main/crates/tokio/RUSTSEC-2021-0072.md
- https://rustsec.org/advisories/RUSTSEC-2021-0072.html
