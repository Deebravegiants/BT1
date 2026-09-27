# [H] CVE-2022-30065

## Summary
Severity: High
Advisory: CVE-2022-30065
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-05-18
Source: https://osv.dev/vulnerability/CVE-2022-30065
Type: osv

## Details
A use-after-free in Busybox 1.35-x's awk applet leads to denial of service and possibly code execution when processing a crafted awk pattern in the copyvar function.

## References
- https://bugs.busybox.net/show_bug.cgi?id=14781
- https://cert-portal.siemens.com/productcert/pdf/ssa-333517.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/30xxx/CVE-2022-30065.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-30065
