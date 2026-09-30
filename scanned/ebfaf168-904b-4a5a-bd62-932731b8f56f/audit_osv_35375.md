# [H] ASoC: SOF: ipc4-topology: Correct the allocation size for bytes controls

## Summary
Severity: High
Advisory: CVE-2025-71286
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2025-71286
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.4.0 <6.6.128, >=6.7.0 <6.12.75, >=6.13.0 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: ipc4-topology: Correct the allocation size for bytes controls

The size of the data behind of scontrol->ipc_control_data for bytes
controls is:
[1] sizeof(struct sof_ipc4_control_data) + // kernel only struct
[2] sizeof(struct sof_abi_hdr)) + payload

The max_size specifies the size of [2] and it is coming from topology.

Change the function to take this into account and allocate adequate amount
of memory behind scontrol->ipc_control_data.

With the change we will allocate [1] amount more memory to be able to hold
the full size of data.

## References
- https://git.kernel.org/stable/c/1237cd9ff198cb882402572f29569e5247190974
- https://git.kernel.org/stable/c/491956b45b5f4933632ea6d8a8bdfdf045ab81e1
- https://git.kernel.org/stable/c/59fe643f21b9d59bcbedb0dfbf988ee455c23736
- https://git.kernel.org/stable/c/a653820700b81c9e6f05ac23b7969ecec1a18e85
- https://git.kernel.org/stable/c/a704a1a4394b5877b9adc31b2c3165ad0b541896
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71286.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-71286
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
