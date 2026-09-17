# [M] CVE-2026-45820

## Summary
Severity: Medium
Advisory: CVE-2026-45820
Aliases: GHSA-px8p-9vwx-vf98
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U/S:N/AU:Y/R:U/V:D/RE:M/U:Amber)
Published: 2026-07-22
Source: https://osv.dev/vulnerability/CVE-2026-45820
Type: osv

## Details
fflate through 0.8.2 is vulnerable to denial of service via an infinite loop in unzipSync(). A crafted ZIP archive with a central directory entry declaring compressed_size=0xFFFFFFFF (ZIP64 sentinel) but missing the required ZIP64 extra field tag 0x0001 causes z64e() to loop indefinitely due to out-of-bounds reads returning undefined, which coerces to 0, keeping the loop condition permanently true.

## References
- https://github.com/101arrowz/fflate/blob/f7873560ad229c22c4b23b06c6a3806ffde77569/src/index.ts#L2714
- https://www.npmjs.com/package/fflate
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45820.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-45820
