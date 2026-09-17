# [M] CVE-2023-4155

## Summary
Severity: Medium
Advisory: CVE-2023-4155
CVSS: 5.6 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2023-09-13
Source: https://osv.dev/vulnerability/CVE-2023-4155
Type: osv

## Details
A flaw was found in KVM AMD Secure Encrypted Virtualization (SEV) in the Linux kernel. A KVM guest using SEV-ES or SEV-SNP with multiple vCPUs can trigger a double fetch race condition vulnerability and invoke the `VMGEXIT` handler recursively. If an attacker manages to call the handler multiple times, they can trigger a stack overflow and cause a denial of service or potentially guest-to-host escape in kernel configurations without stack guard pages (`CONFIG_VMAP_STACK`).

## References
- https://access.redhat.com/security/cve/CVE-2023-4155
- https://bugzilla.redhat.com/show_bug.cgi?id=2213802
