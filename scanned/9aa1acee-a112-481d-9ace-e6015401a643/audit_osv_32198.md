# [M] CVE-2025-25724

## Summary
Severity: Medium
Advisory: CVE-2025-25724
CVSS: 4.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L)
Published: 2025-03-02
Source: https://osv.dev/vulnerability/CVE-2025-25724
Type: osv

## Details
list_item_verbose in tar/util.c in libarchive through 3.7.7 does not check an strftime return value, which can lead to a denial of service or unspecified other impact via a crafted TAR archive that is read with a verbose value of 2. For example, the 100-byte buffer may not be sufficient for a custom locale.

## References
- https://gist.github.com/Ekkosun/a83870ce7f3b7813b9b462a395e8ad92
- https://github.com/Ekkosun/pocs/blob/main/bsdtarbug
- https://github.com/libarchive/libarchive/blob/b439d586f53911c84be5e380445a8a259e19114c/tar/util.c#L751-L752
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25724.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25724
