# [H] drm/amd/display: Fix out-of-bound accesses

## Summary
Severity: High
Advisory: CVE-2025-21985
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-01
Source: https://osv.dev/vulnerability/CVE-2025-21985
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.12.20, >=6.13.0 <6.13.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Fix out-of-bound accesses

[WHAT & HOW]
hpo_stream_to_link_encoder_mapping has size MAX_HPO_DP2_ENCODERS(=4),
but location can have size up to 6. As a result, it is necessary to
check location against MAX_HPO_DP2_ENCODERS.

Similiarly, disp_cfg_stream_location can be used as an array index which
should be 0..5, so the ASSERT's conditions should be less without equal.

## References
- https://git.kernel.org/stable/c/36793d90d76f667d26c6dd025571481ee0c96abc
- https://git.kernel.org/stable/c/8adbb2a98b00926315fd513b5fe2596b5716b82d
- https://git.kernel.org/stable/c/9aedc776b11038f04f4641241bb7e877781e4aa4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/21xxx/CVE-2025-21985.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-21985
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
