# [H] ethtool: cmis: validate start_cmd_payload_size from module

## Summary
Severity: High
Advisory: CVE-2026-63995
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63995
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.11.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

ethtool: cmis: validate start_cmd_payload_size from module

The CMIS firmware update code reads start_cmd_payload_size from
the module's FW Management Features CDB reply and uses it directly
as the byte count for memcpy. The destination buffer is 112 bytes
(ETHTOOL_CMIS_CDB_LPL_MAX_PL_LENGTH - 8). So a malicious
module (or corrupted response) can cause a OOB write later on in
cmis_fw_update_start_download().

Let's error out. If modules that expect longer LPL writes actually
exist we should revisit.

struct cmis_cdb_start_fw_download_pl's definition has to move,
no change there.

## References
- https://git.kernel.org/stable/c/0696709e951be54c699664adf546d16e28974d53
- https://git.kernel.org/stable/c/12c2496a71f82f63617971ca9b730dffa05cf58b
- https://git.kernel.org/stable/c/63112b4515469d00008452d9cfe3fb3bf1aa2df3
- https://git.kernel.org/stable/c/a46340da00385be7fb16c62425ebc20006f2d5d8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63995.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63995
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
