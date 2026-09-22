# [C] CVE-2019-10063

## Summary
Severity: Critical
Advisory: CVE-2019-10063
CVSS: 9.0 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2019-03-26
Source: https://osv.dev/vulnerability/CVE-2019-10063
Type: osv

## Details
Flatpak before 1.0.8, 1.1.x and 1.2.x before 1.2.4, and 1.3.x before 1.3.1 allows a sandbox bypass. Flatpak versions since 0.8.1 address CVE-2017-5226 by using a seccomp filter to prevent sandboxed apps from using the TIOCSTI ioctl, which could otherwise be used to inject commands into the controlling terminal so that they would be executed outside the sandbox after the sandboxed app exits. This fix was incomplete: on 64-bit platforms, the seccomp filter could be bypassed by an ioctl request number that has TIOCSTI in its 32 least significant bits and an arbitrary nonzero value in its 32 most significant bits, which the Linux kernel would treat as equivalent to TIOCSTI.

## References
- https://access.redhat.com/errata/RHSA-2019:1024
- https://access.redhat.com/errata/RHSA-2019:1143
- https://github.com/flatpak/flatpak/issues/2782
