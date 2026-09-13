# [H] CVE-2023-2006

## Summary
Severity: High
Advisory: CVE-2023-2006
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/CVE-2023-2006
Type: osv

## Details
A race condition was found in the Linux kernel's RxRPC network protocol, within the processing of RxRPC bundles. This issue results from the lack of proper locking when performing operations on an object. This may allow an attacker to escalate privileges and execute arbitrary code in the context of the kernel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2006.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2006
- https://security.netapp.com/advisory/ntap-20230609-0004/
- https://www.zerodayinitiative.com/advisories/ZDI-23-439/
- https://bugzilla.redhat.com/show_bug.cgi?id=2189112
- https://github.com/torvalds/linux/commit/3bcd6c7eaa53
