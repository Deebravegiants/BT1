# [C] Apache CloudStack: Proxmox Extension Allows Unauthorized Cross-Tenant Instance Access

## Summary
Severity: Critical
Advisory: CVE-2026-25199
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-25199
Type: osv

## Details
Instances deployed via the Proxmox extension allow unauthorized access to instances belonging to other tenants.




This issue affects Apache CloudStack: from 4.21.0.0 through 4.22.0.0.




The Proxmox extension for CloudStack improperly uses a user-editable instance setting, proxmox_vmid, to associate CloudStack instances with Proxmox virtual machines. Because this value is not restricted or validated against tenant ownership and Proxmox VM IDs are predictable, a non-privileged attacker can modify the setting to reference a VM belonging to another account. This allows unauthorized cross-tenant access and enables full control over the targeted VM, including starting, stopping, and destroying the virtual machine.




Users are recommended to upgrade to version 4.22.0.1, which fixes this issue.




As a workaround for the existing installations, editing of the proxmox_vmid instance detail by users can be prevented by adding this detail name to the global configuration parameter - user.vm.denied.details.

## References
- http://www.openwall.com/lists/oss-security/2026/05/09/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25199.json
- https://lists.apache.org/thread/n8mt5b7wkpysstb8w7rr9f02kc5cq2xm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25199
