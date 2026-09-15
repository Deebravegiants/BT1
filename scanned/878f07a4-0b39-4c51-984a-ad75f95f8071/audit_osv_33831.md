# [H] CVE-2025-51006

## Summary
Severity: High
Advisory: CVE-2025-51006
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-22
Source: https://osv.dev/vulnerability/CVE-2025-51006
Type: osv

## Details
Within tcpreplay's tcprewrite, a double free vulnerability has been identified in the dlt_linuxsll2_cleanup() function in plugins/dlt_linuxsll2/linuxsll2.c. This vulnerability is triggered when tcpedit_dlt_cleanup() indirectly invokes the cleanup routine multiple times on the same memory region. By supplying a specifically crafted pcap file to the tcprewrite binary, a local attacker can exploit this flaw to cause a Denial of Service (DoS) via memory corruption.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/51xxx/CVE-2025-51006.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-51006
- https://github.com/appneta/tcpreplay/issues/926
- https://github.com/sy460129/CVE-2025-51006
