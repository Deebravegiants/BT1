# [M] CVE-2025-29491

## Summary
Severity: Medium
Advisory: CVE-2025-29491
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2025-29491
Type: osv

## Details
An allocation-size-too-big error in the parseSWF_DEFINEBINARYDATA function of libming v0.48 allows attackers to cause a Denial of Service (DoS) via supplying a crafted SWF file.

## References
- https://github.com/goodmow/PoC/blob/main/libming/libming-fuzz10.readme
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/29xxx/CVE-2025-29491.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-29491
- https://github.com/libming/libming/issues/330
