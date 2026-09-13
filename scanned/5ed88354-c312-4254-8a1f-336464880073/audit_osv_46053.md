# [M] A malicious client acting as the receiver of an rsync file transfer can trigger an out of bounds...

## Summary
Severity: Medium
Advisory: JLSEC-2026-625
Ecosystem: Julia
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/JLSEC-2026-625
Type: osv

## Affected
- Julia: `rsync_jll` — affected >=0 <3.4.4+0

## Details
A malicious client acting as the receiver of an rsync file transfer can trigger an out of bounds read of a heap based buffer, via a negative array index. The

malicious

rsync client requires at least read access to the remote rsync module in order to trigger the issue.

## References
- https://attackerkb.com/assessments/fbacb2a6-d1cd-4011-bb3a-f06b1c8306b1
- https://github.com/RsyncProject/rsync/commit/797e17fc4a6f15e3b1756538a9f812b63942686f
- https://github.com/advisories/GHSA-3rvc-qcwh-fhqv
- https://nvd.nist.gov/vuln/detail/CVE-2025-10158
