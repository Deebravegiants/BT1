# [C] Apache Arrow R package: Arbitrary code execution when loading a malicious data file

## Summary
Severity: Critical
Advisory: CVE-2024-52338
Aliases: PYSEC-2024-161
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-28
Source: https://osv.dev/vulnerability/CVE-2024-52338
Type: osv

## Details
Deserialization of untrusted data in IPC and Parquet readers in the Apache Arrow R package versions 4.0.0 through 16.1.0 allows arbitrary code execution. An application is vulnerable if it 
reads Arrow IPC, Feather or Parquet data from untrusted sources (for 
example, user-supplied input files). This vulnerability only affects the arrow R package, not other Apache Arrow 
implementations or bindings unless those bindings are specifically used via the R package (for example, an R application that embeds a Python interpreter and uses PyArrow to read files from untrusted sources is still vulnerable if the arrow R package is an affected version). It is recommended that users of the arrow R package upgrade to 17.0.0 or later. Similarly, it
 is recommended that downstream libraries upgrade their dependency 
requirements to arrow 17.0.0 or later. If using an affected
version of the package, untrusted data can read into a Table and its internal to_data_frame() method can be used as a workaround (e.g., read_parquet(..., as_data_frame = FALSE)$to_data_frame()).


This issue affects the Apache Arrow R package: from 4.0.0 through 16.1.0.


Users are recommended to upgrade to version 17.0.0, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2024/11/28/3
- https://cran.r-project.org/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/52xxx/CVE-2024-52338.json
- https://lists.apache.org/thread/0rcbvj1gdp15lvm23zm601tjpq0k25vt
- https://nvd.nist.gov/vuln/detail/CVE-2024-52338
- https://github.com/apache/arrow/commit/801de2fbcf5bcbce0c019ed4b35ff3fc863b141b
