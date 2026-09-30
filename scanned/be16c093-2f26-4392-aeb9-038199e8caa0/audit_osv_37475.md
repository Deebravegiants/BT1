# [H] rxrpc: only handle RESPONSE during service challenge

## Summary
Severity: High
Advisory: CVE-2026-31676
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-04-25
Source: https://osv.dev/vulnerability/CVE-2026-31676
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.23, >=6.19.0 <6.19.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

rxrpc: only handle RESPONSE during service challenge

Only process RESPONSE packets while the service connection is still in
RXRPC_CONN_SERVICE_CHALLENGING. Check that state under state_lock before
running response verification and security initialization, then use a local
secured flag to decide whether to queue the secured-connection work after
the state transition. This keeps duplicate or late RESPONSE packets from
re-running the setup path and removes the unlocked post-transition state
test.

## References
- https://git.kernel.org/stable/c/03fd2ef73cb4ffd0af100a95b634af54f474414e
- https://git.kernel.org/stable/c/0afdfd4941c1b60a1f5c361760daa970edca60cd
- https://git.kernel.org/stable/c/29b44d904dceb832be880def08b8cb17a0aba91c
- https://git.kernel.org/stable/c/6c3a0fbdafef8316e34ae22333e317a341e737cd
- https://git.kernel.org/stable/c/a1a8efde03a40b6c658d580e96644d9b9a2a0d3a
- https://git.kernel.org/stable/c/a6bcf8010af093fe04f7100562e9542ab7882585
- https://git.kernel.org/stable/c/c43ffdcfdbb5567b1f143556df8a04b4eeea041c
- https://git.kernel.org/stable/c/d0035e634dae83237ab7f5681eb52b2f65d0ceb8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31676.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31676
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
