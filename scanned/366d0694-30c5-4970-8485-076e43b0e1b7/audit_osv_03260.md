# [M] ALPINE-CVE-2025-31498

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-31498
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X)
Published: 2025-04-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-31498
Type: osv

## Affected
- Alpine:v3.21: `c-ares` — affected >=0 <1.34.5-r0
- Alpine:v3.22: `c-ares` — affected >=0 <1.34.5-r0
- Alpine:v3.23: `c-ares` — affected >=0 <1.34.5-r0
- Alpine:v3.24: `c-ares` — affected >=0 <1.34.5-r0

## Details
c-ares is an asynchronous resolver library. From 1.32.3 through 1.34.4, there is a use-after-free in read_answers() when process_answer() may re-enqueue a query either due to a DNS Cookie Failure or when the upstream server does not properly support EDNS, or possibly on TCP queries if the remote closed the connection immediately after a response. If there was an issue trying to put that new transaction on the wire, it would close the connection handle, but read_answers() was still expecting the connection handle to be available to possibly dequeue other responses. In theory a remote attacker might be able to trigger this by flooding the target with ICMP UNREACHABLE packets if they also control the upstream nameserver and can return a result with one of those conditions, this has been untested. Otherwise only a local attacker might be able to change system behavior to make send()/write() return a failure condition. This vulnerability is fixed in 1.34.5.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-31498
