# [M] HDF5 SOHM List Index Heap Buffer Overflow

## Summary
Severity: Medium
Advisory: CVE-2026-17572
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:H/SC:N/SI:L/SA:H/E:U)
Published: 2026-07-27
Source: https://osv.dev/vulnerability/CVE-2026-17572
Type: osv

## Details
Heap-based buffer overflow in the SOHM list-index deserialization code in HDF5 through 2.1.1 on all platforms allows attackers to cause a denial of service (crash) via a crafted HDF5 file whose shared-message list index declares a num_messages count exceeding list_max, triggering out-of-bounds heap reads and writes in H5SM__cache_list_deserialize and H5SM__cache_list_verify_chksum.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/17xxx/CVE-2026-17572.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-17572
- https://github.com/HDFGroup/hdf5/issues/6501
