# [H] github.com/ulikunitz/xz fixes readUvarint Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-25xm-hr59-7c27
CVE: CVE-2021-29482
CWE: CWE-835
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-05-25
Source: https://github.com/advisories/GHSA-25xm-hr59-7c27
Type: github-advisory

## Affected
- Go: `github.com/ulikunitz/xz` — affected >=0 <0.5.8

## Details
### Impact

xz is a compression and decompression library focusing on the xz format completely written in Go. The function readUvarint used to read the xz container format may not terminate a loop provide malicous input.

### Patches

The problem has been fixed in release v0.5.8.

### Workarounds

Limit the size of the compressed file input to a reasonable size for your use case.

### References

The standard library had recently the same issue and got the [CVE-2020-16845](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2020-16845) allocated.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [xz](https://github.com/ulikunitz/xz/issues).

## References
- https://github.com/ulikunitz/xz/security/advisories/GHSA-25xm-hr59-7c27
- https://nvd.nist.gov/vuln/detail/CVE-2021-29482
- https://github.com/ulikunitz/xz/issues/35
- https://github.com/ulikunitz/xz/commit/69c6093c7b2397b923acf82cb378f55ab2652b9b
- https://pkg.go.dev/vuln/GO-2020-0016
