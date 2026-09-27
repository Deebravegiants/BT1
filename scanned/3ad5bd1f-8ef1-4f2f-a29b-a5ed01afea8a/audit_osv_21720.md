# [M] CVE-2021-45931

## Summary
Severity: Medium
Advisory: CVE-2021-45931
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-01
Source: https://osv.dev/vulnerability/CVE-2021-45931
Type: osv

## Details
HarfBuzz 2.9.0 has an out-of-bounds write in hb_bit_set_invertible_t::set (called from hb_sparseset_t<hb_bit_set_invertible_t>::set and hb_set_copy).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4EAIZKL4O67FN2CWJYHYKZEMNYWNWO3D/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/5A7TCR2MY46YK3NHQZB3SLESUH354IEA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DI6247WOAKB46CZZ6SCDSJVWWCW3GMZH/
- https://security.gentoo.org/glsa/202209-11
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=37425
- https://github.com/harfbuzz/harfbuzz/commit/d3e09bf4654fe5478b6dbf2b26ebab6271317d81
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/harfbuzz/OSV-2021-1159.yaml
