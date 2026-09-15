# [M] CVE-2023-46841

## Summary
Severity: Medium
Advisory: CVE-2023-46841
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2024-03-20
Source: https://osv.dev/vulnerability/CVE-2023-46841
Type: osv

## Details
Recent x86 CPUs offer functionality named Control-flow Enforcement
Technology (CET).  A sub-feature of this are Shadow Stacks (CET-SS).
CET-SS is a hardware feature designed to protect against Return Oriented
Programming attacks. When enabled, traditional stacks holding both data
and return addresses are accompanied by so called "shadow stacks",
holding little more than return addresses.  Shadow stacks aren't
writable by normal instructions, and upon function returns their
contents are used to check for possible manipulation of a return address
coming from the traditional stack.

In particular certain memory accesses need intercepting by Xen.  In
various cases the necessary emulation involves kind of replaying of
the instruction.  Such replaying typically involves filling and then
invoking of a stub.  Such a replayed instruction may raise an
exceptions, which is expected and dealt with accordingly.

Unfortunately the interaction of both of the above wasn't right:
Recovery involves removal of a call frame from the (traditional) stack.
The counterpart of this operation for the shadow stack was missing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HES2IJXZY3H7HBPP4NVSVYYNGW254DMI/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZON4TLXG7TG4A2XZG563JMVTGQW4SF3A/
- https://xenbits.xenproject.org/xsa/advisory-451.html
- http://xenbits.xen.org/xsa/advisory-451.html
