# [H] soundwire: qcom: fix storing port config out-of-bounds

## Summary
Severity: High
Advisory: CVE-2023-53465
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2023-53465
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.13.0 <5.15.121, >=5.16.0 <6.1.40, >=6.2.0 <6.4.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

soundwire: qcom: fix storing port config out-of-bounds

The 'qcom_swrm_ctrl->pconfig' has size of QCOM_SDW_MAX_PORTS (14),
however we index it starting from 1, not 0, to match real port numbers.
This can lead to writing port config past 'pconfig' bounds and
overwriting next member of 'qcom_swrm_ctrl' struct.  Reported also by
smatch:

  drivers/soundwire/qcom.c:1269 qcom_swrm_get_port_config() error: buffer overflow 'ctrl->pconfig' 14 <= 14

## References
- https://git.kernel.org/stable/c/20f7c4d51c94abb1a1a7c21900db4fb5afe5c8ff
- https://git.kernel.org/stable/c/32eb67d7360d48c15883e0d21b29c0aab9da022e
- https://git.kernel.org/stable/c/490937d479abe5f6584e69b96df066bc87be92e9
- https://git.kernel.org/stable/c/801daff0078087b5df9145c9f5e643c28129734b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53465.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53465
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
