# [H] terraform-provider-proxmox has insecure sudo recommendation in the documentation

## Summary
Severity: High
Advisory: GHSA-gwch-7m8v-7544
CVE: CVE-2026-25499
CWE: CWE-1188, CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-gwch-7m8v-7544
Type: github-advisory

## Affected
- Go: `github.com/bpg/terraform-provider-proxmox` — affected >=0 <0.93.1

## Details
> Note: It is uncertain whether this constitutes a vulnerability or should be filed as an issue instead.

### Summary

In the SSH configuration documentation, the sudoer line that was suggested can be escalated to edit any files in the system.

### Details

The following line were suggested for addition in the sudoers file:

```bash
terraform ALL=(root) NOPASSWD: /usr/bin/tee /var/lib/vz/*
```

But this is highly insecure as  the folder can be escaped using `../` and any files can be edited on the system.

### PoC

Using a `terraform` user with the previously mentioned line in the `/etc/sudoers` file, a `/etc/sudoers.d/sudo` file can be added using this command:

`echo "ALL=(ALL) NOPASSWD:ALL" | tee /var/lib/vz/../../../etc/sudoers.d/sudo`

This grants access to the full root of the node.

### Impact

This breaches the access limits of the Terraform user.

### Suggested workaround

Use a strict regex on the command to allow only the names that should be pushed by this user.

Example for cloudinit yaml files:

```bash
terraform ALL=(root) NOPASSWD: /usr/bin/tee /var/lib/vz/snippets/[A-Za-z0-9-]*\\.yaml
```

## References
- https://github.com/bpg/terraform-provider-proxmox/security/advisories/GHSA-gwch-7m8v-7544
- https://nvd.nist.gov/vuln/detail/CVE-2026-25499
- https://github.com/bpg/terraform-provider-proxmox/commit/bd604c41a31e2a55dd6acc01b0608be3ea49c023
- https://github.com/bpg/terraform-provider-proxmox
