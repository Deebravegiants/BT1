# [M] CVE-2023-34328

## Summary
Severity: Medium
Advisory: CVE-2023-34328
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/CVE-2023-34328
Type: osv

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

AMD CPUs since ~2014 have extensions to normal x86 debugging functionality.
Xen supports guests using these extensions.

Unfortunately there are errors in Xen's handling of the guest state, leading
to denials of service.

 1) CVE-2023-34327 - An HVM vCPU can end up operating in the context of
    a previous vCPUs debug mask state.

 2) CVE-2023-34328 - A PV vCPU can place a breakpoint over the live GDT.
    This allows the PV vCPU to exploit XSA-156 / CVE-2015-8104 and lock
    up the CPU entirely.

## References
- http://xenbits.xen.org/xsa/advisory-444.html
- https://xenbits.xenproject.org/xsa/advisory-444.html
