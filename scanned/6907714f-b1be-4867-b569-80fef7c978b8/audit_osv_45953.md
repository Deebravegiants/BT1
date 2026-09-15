# [M] JLSEC-2026-514

## Summary
Severity: Medium
Advisory: JLSEC-2026-514
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/JLSEC-2026-514
Type: osv

## Affected
- Julia: `ZeroMQ_jll` — affected >=0 <4.3.4+0

## Details
An uncontrolled resource consumption (memory leak) flaw was found in the ZeroMQ client in versions before 4.3.3 in `src/pipe.cpp`. This issue causes a client that connects to multiple malicious or compromised servers to crash. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1921972
- https://github.com/zeromq/libzmq/security/advisories/GHSA-wfr2-29gj-5w87
