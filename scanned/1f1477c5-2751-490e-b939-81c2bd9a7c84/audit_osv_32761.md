# [H] pds_core: handle unsupported PDS_CORE_CMD_FW_CONTROL result

## Summary
Severity: High
Advisory: CVE-2025-37887
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2025-05-09
Source: https://osv.dev/vulnerability/CVE-2025-37887
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.89, >=6.7.0 <6.12.26, >=6.13.0 <6.14.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

pds_core: handle unsupported PDS_CORE_CMD_FW_CONTROL result

If the FW doesn't support the PDS_CORE_CMD_FW_CONTROL command
the driver might at the least print garbage and at the worst
crash when the user runs the "devlink dev info" devlink command.

This happens because the stack variable fw_list is not 0
initialized which results in fw_list.num_fw_slots being a
garbage value from the stack.  Then the driver tries to access
fw_list.fw_names[i] with i >= ARRAY_SIZE and runs off the end
of the array.

Fix this by initializing the fw_list and by not failing
completely if the devcmd fails because other useful information
is printed via devlink dev info even if the devcmd fails.

## References
- https://git.kernel.org/stable/c/12a4651a80dbe4589a84e26785fbbe1ed4d043b7
- https://git.kernel.org/stable/c/2567daad69cd1107fc0ec29b1615f110d7cf7385
- https://git.kernel.org/stable/c/6702f5c6b22deaa95bf84f526148174a160a02cb
- https://git.kernel.org/stable/c/cdd784c96fe2e5edbf0ed9b3e96fe776e8092385
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37887.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
