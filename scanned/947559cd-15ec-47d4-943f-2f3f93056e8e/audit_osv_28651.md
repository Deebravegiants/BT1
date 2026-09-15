# [C] wifi: iwlwifi: dbg-tlv: ensure NUL termination

## Summary
Severity: Critical
Advisory: CVE-2024-35845
Ecosystem: Linux
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35845
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: dbg-tlv: ensure NUL termination

The iwl_fw_ini_debug_info_tlv is used as a string, so we must
ensure the string is terminated correctly before using it.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/71d4186d470e9cda7cd1a0921b4afda737c6f641
- https://git.kernel.org/stable/c/783d413f332a3ebec916664b366c28f58147f82c
- https://git.kernel.org/stable/c/96aa40761673da045a7774f874487cdb50c6a2f7
- https://git.kernel.org/stable/c/c855a1a5b7e3de57e6b1b29563113d5e3bfdb89a
- https://git.kernel.org/stable/c/ea1d166fae14e05d49ffb0ea9fcd4658f8d3dcea
- https://git.kernel.org/stable/c/fabe2db7de32a881e437ee69db32e0de785a6209
- https://git.kernel.org/stable/c/fec14d1cdd92f340b9ba2bd220abf96f9609f2a9
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35845.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35845
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
