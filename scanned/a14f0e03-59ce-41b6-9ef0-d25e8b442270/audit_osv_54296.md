# [M] CVE-2023-46842

## Summary
Severity: Medium
Advisory: CVE-2023-46842
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-05-16
Source: https://osv.dev/vulnerability/CVE-2023-46842
Type: osv

## Details
Unlike 32-bit PV guests, HVM guests may switch freely between 64-bit and
other modes.  This in particular means that they may set registers used
to pass 32-bit-mode hypercall arguments to values outside of the range
32-bit code would be able to set them to.

When processing of hypercalls takes a considerable amount of time,
the hypervisor may choose to invoke a hypercall continuation.  Doing so
involves putting (perhaps updated) hypercall arguments in respective
registers.  For guests not running in 64-bit mode this further involves
a certain amount of translation of the values.

Unfortunately internal sanity checking of these translated values
assumes high halves of registers to always be clear when invoking a
hypercall.  When this is found not to be the case, it triggers a
consistency check in the hypervisor and causes a crash.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D5OK6MH75S7YWD34EWW7QIZTS627RIE3/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/RYAZ7P6YFJ2E3FHKAGIKHWS46KYMMTZH/
- https://xenbits.xenproject.org/xsa/advisory-454.html
- http://xenbits.xen.org/xsa/advisory-454.html
