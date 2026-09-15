# [H] i40e: fix race condition by adding filter's intermediate sync state

## Summary
Severity: High
Advisory: CVE-2024-53088
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-53088
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.10.0 <5.15.172, >=5.16.0 <6.1.117, >=6.2.0 <6.6.61, >=6.7.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

i40e: fix race condition by adding filter's intermediate sync state

Fix a race condition in the i40e driver that leads to MAC/VLAN filters
becoming corrupted and leaking. Address the issue that occurs under
heavy load when multiple threads are concurrently modifying MAC/VLAN
filters by setting mac and port VLAN.

1. Thread T0 allocates a filter in i40e_add_filter() within
        i40e_ndo_set_vf_port_vlan().
2. Thread T1 concurrently frees the filter in __i40e_del_filter() within
        i40e_ndo_set_vf_mac().
3. Subsequently, i40e_service_task() calls i40e_sync_vsi_filters(), which
        refers to the already freed filter memory, causing corruption.

Reproduction steps:
1. Spawn multiple VFs.
2. Apply a concurrent heavy load by running parallel operations to change
        MAC addresses on the VFs and change port VLANs on the host.
3. Observe errors in dmesg:
"Error I40E_AQ_RC_ENOSPC adding RX filters on VF XX,
	please set promiscuous on manually for VF XX".

Exact code for stable reproduction Intel can't open-source now.

The fix involves implementing a new intermediate filter state,
I40E_FILTER_NEW_SYNC, for the time when a filter is on a tmp_add_list.
These filters cannot be deleted from the hash list directly but
must be removed using the full process.

## References
- https://git.kernel.org/stable/c/262dc6ea5f1eb18c4d08ad83d51222d0dd0dd42a
- https://git.kernel.org/stable/c/6e046f4937474bc1b9fa980c1ad8f3253fc638f6
- https://git.kernel.org/stable/c/7ad3fb3bfd43feb4e15c81dffd23ac4e55742791
- https://git.kernel.org/stable/c/bf5f837d9fd27d32fb76df0a108babcaf4446ff1
- https://git.kernel.org/stable/c/f30490e9695ef7da3d0899c6a0293cc7cd373567
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53088.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53088
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
