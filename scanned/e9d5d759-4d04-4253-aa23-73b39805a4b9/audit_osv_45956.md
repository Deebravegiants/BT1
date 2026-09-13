# [H] JLSEC-2026-517

## Summary
Severity: High
Advisory: JLSEC-2026-517
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-20
Source: https://osv.dev/vulnerability/JLSEC-2026-517
Type: osv

## Affected
- Julia: `ZeroMQ_jll` — affected >=0 <4.3.4+0

## Details
An uncontrolled resource consumption (memory leak) flaw was found in ZeroMQ's `src/xpub.cpp` in versions before 4.3.3. This flaw allows a remote unauthenticated attacker to send crafted PUB messages that consume excessive memory if the CURVE/ZAP authentication is disabled on the server, causing a denial of service. The highest threat from this vulnerability is to system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1921989
- https://github.com/zeromq/libzmq/security/advisories/GHSA-4p5v-h92w-6wxw
