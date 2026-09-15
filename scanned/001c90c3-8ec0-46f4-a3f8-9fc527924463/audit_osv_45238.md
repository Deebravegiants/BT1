# [H] `list_item_verbose` in `tar/util.c` in libarchive through 3.7.7 does not check an strftime return...

## Summary
Severity: High
Advisory: JLSEC-2025-243
Ecosystem: Julia
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-11-25
Source: https://osv.dev/vulnerability/JLSEC-2025-243
Type: osv

## Affected
- Julia: `LibArchive_jll` — affected >=0 <3.7.9+0

## Details
`list_item_verbose` in `tar/util.c` in libarchive through 3.7.7 does not check an strftime return value, which can lead to a denial of service or unspecified other impact via a crafted TAR archive that is read with a verbose value of 2. For example, the 100-byte buffer may not be sufficient for a custom locale.

## References
- https://gist.github.com/Ekkosun/a83870ce7f3b7813b9b462a395e8ad92
- https://github.com/Ekkosun/pocs/blob/main/bsdtarbug
- https://github.com/advisories/GHSA-722w-734r-qg74
- https://github.com/libarchive/libarchive/blob/b439d586f53911c84be5e380445a8a259e19114c/tar/util.c#L751-L752
- https://nvd.nist.gov/vuln/detail/CVE-2025-25724
