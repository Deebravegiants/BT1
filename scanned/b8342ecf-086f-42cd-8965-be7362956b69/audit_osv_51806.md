# [H] CVE-2021-4093

## Summary
Severity: High
Advisory: CVE-2021-4093
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-02-18
Source: https://osv.dev/vulnerability/CVE-2021-4093
Type: osv

## Details
A flaw was found in the KVM's AMD code for supporting the Secure Encrypted Virtualization-Encrypted State (SEV-ES). A KVM guest using SEV-ES can trigger out-of-bounds reads and writes in the host kernel via a malicious VMGEXIT for a string I/O instruction (for example, outs or ins) using the exit reason SVM_EXIT_IOIO. This issue results in a crash of the entire system or a potential guest-to-host escape scenario.

## References
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2222
- https://bugzilla.redhat.com/show_bug.cgi?id=2028584
