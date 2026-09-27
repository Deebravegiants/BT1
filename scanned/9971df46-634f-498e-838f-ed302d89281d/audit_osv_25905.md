# [H] CVE-2023-47016

## Summary
Severity: High
Advisory: CVE-2023-47016
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-22
Source: https://osv.dev/vulnerability/CVE-2023-47016
Type: osv

## Details
radare2 5.8.9 has an out-of-bounds read in r_bin_object_set_items in libr/bin/bobj.c, causing a crash in r_read_le32 in libr/include/r_endian.h.

## References
- https://gist.github.com/gandalf4a/65705be4f84269cb7cd725a1d4ab2ffa
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/47xxx/CVE-2023-47016.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-47016
- https://github.com/radareorg/radare2/issues/22349
- https://github.com/radareorg/radare2/commit/40c9f50e127be80b9d816bce2ab2ee790831aefd
