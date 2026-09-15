# [H] ice: fix using untrusted value of pkt_len in ice_vc_fdir_parse_raw()

## Summary
Severity: High
Advisory: CVE-2025-22117
Ecosystem: Linux
CVSS: 8.7 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:H)
Published: 2025-04-16
Source: https://osv.dev/vulnerability/CVE-2025-22117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.80, >=6.13.0 <6.14.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ice: fix using untrusted value of pkt_len in ice_vc_fdir_parse_raw()

Fix using the untrusted value of proto->raw.pkt_len in function
ice_vc_fdir_parse_raw() by verifying if it does not exceed the
VIRTCHNL_MAX_SIZE_RAW_PACKET value.

## References
- https://git.kernel.org/stable/c/1388dd564183a5a18ec4a966748037736b5653c5
- https://git.kernel.org/stable/c/362f704ba73a359db9cded567e891d9a8f081875
- https://git.kernel.org/stable/c/363377af2c9e874fbba3a199408f8ec7b37906f7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22117.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-22117
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
