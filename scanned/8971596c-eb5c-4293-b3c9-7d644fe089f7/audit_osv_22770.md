# [H] CVE-2022-3872

## Summary
Severity: High
Advisory: CVE-2022-3872
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-07
Source: https://osv.dev/vulnerability/CVE-2022-3872
Type: osv

## Details
An off-by-one read/write issue was found in the SDHCI device of QEMU. It occurs when reading/writing the Buffer Data Port Register in sdhci_read_dataport and sdhci_write_dataport, respectively, if data_count == block_size. A malicious guest could use this flaw to crash the QEMU process on the host, resulting in a denial of service condition.

## References
- https://lists.nongnu.org/archive/html/qemu-devel/2022-11/msg01068.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3872.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3872
- https://security.netapp.com/advisory/ntap-20221215-0005/
