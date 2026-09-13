# [C] batman-adv: tt: prevent TVLV OOB check overflow

## Summary
Severity: Critical
Advisory: CVE-2026-72226
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72226
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

batman-adv: tt: prevent TVLV OOB check overflow

A TT unicast TVLV contains the number of VLANs stored in it. This number is
an u16 and gets multiplied by the size of the struct
batadv_tvlv_tt_vlan_data (8 bytes). The size can therefore overflow the u16
used to store the tt_vlan_len. All additional safety checks to prevent
out-of-bounds access of the TVLV buffer are invalid due to this overflow.

Using size_t prevents this overflow and ensures that the safety checks
compare against the actual buffer requirements.

## References
- https://git.kernel.org/stable/c/0de12a4c4847f571d82a9cd96bc633eded41d7c6
- https://git.kernel.org/stable/c/1898273c5dc8148267ef9f97cd2517a2822350e7
- https://git.kernel.org/stable/c/3256c05d5a9db34346eaf20f52dddde984852d77
- https://git.kernel.org/stable/c/604bd5042fbcd1ab9f7cd98fd847ec017aeede8a
- https://git.kernel.org/stable/c/6222b443686525cb5a9b6a9cecf23b2e2ab23e2a
- https://git.kernel.org/stable/c/7319c0794f91be2734aac695794e7203606b49f8
- https://git.kernel.org/stable/c/7a581d9aaba8c82bd6177fa36b2588eea77f6e2b
- https://git.kernel.org/stable/c/d6ff4764ff784ede25f5c83a6f5883a74c93a5ea
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72226.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72226
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
