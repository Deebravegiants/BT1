# [H] CVE-2023-2008

## Summary
Severity: High
Advisory: CVE-2023-2008
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-14
Source: https://osv.dev/vulnerability/CVE-2023-2008
Type: osv

## Details
A flaw was found in the Linux kernel's udmabuf device driver. The specific flaw exists within a fault handler. The issue results from the lack of proper validation of user-supplied data, which can result in a memory access past the end of an array. An attacker can leverage this vulnerability to escalate privileges and execute arbitrary code in the context of the kernel.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/2xxx/CVE-2023-2008.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-2008
- https://security.netapp.com/advisory/ntap-20230517-0007/
- https://www.zerodayinitiative.com/advisories/ZDI-23-441/
- https://bugzilla.redhat.com/show_bug.cgi?id=2186862
- https://github.com/torvalds/linux/commit/05b252cccb2e5c3f56119d25de684b4f810ba4
