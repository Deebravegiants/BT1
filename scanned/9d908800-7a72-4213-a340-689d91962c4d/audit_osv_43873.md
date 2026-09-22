# [M] A Signed Length Overflow in Erlang/OTP's inet TCP Driver Overflows the Receive Buffer Into BEAM VM Memory From an Unauthenticated Peer

## Summary
Severity: Medium
Advisory: CVE-2026-75538
Aliases: EEF-CVE-2026-75538, GHSA-8m6r-2pj2-25pm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-75538
Type: osv

## Details
An attacker that connects to an open Erlang TCP port that uses the inet driver with {packet,4} mode can use a signed overflow in an incorrect packet length calculation to overflow the receive buffer into the VM allocator area and beyond up to about 2 GB.

This would easily trash the allocated block's allocator metadata footer, and the next block, if any, and most likely cause the BEAM VM to crash. Utilizing this with precision enough to achieve Remote Code Execution would be extremely unfeasible.

This issue affects OTP from OTP 17.0 before OTP 27.3.4.17, from OTP 28.0 before OTP 28.5.0.6, and from OTP 29.0 before OTP 29.0.6, corresponding to erts from 6.0 before 15.2.7.13, from 16.0 before 16.4.0.6, and from 17.0 before 17.0.6. Whether OTP before OTP 17.0, corresponding to erts before 6.0, is affected is unknown.

## References
- https://cna.erlef.org/cves/CVE-2026-75538.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-75538
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75538.json
- https://github.com/erlang/otp/security/advisories/GHSA-8m6r-2pj2-25pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-75538
- https://github.com/erlang/otp/commit/08e8efdba8500d2d6f54c6b1de1492b228017c9b
- https://github.com/erlang/otp
