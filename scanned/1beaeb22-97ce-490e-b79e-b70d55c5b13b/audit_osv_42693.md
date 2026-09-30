# [H] imagecli - Uncontrolled Memory Allocation via Unbounded scale Ratio Causes Denial of Service

## Summary
Severity: High
Advisory: CVE-2026-70377
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-70377
Type: osv

## Details
imagecli's pipeline operation (Scale::apply in src/image_ops.rs) computes output width/height as (dimension as f32 * ratio) as u32 with no upper-bound validation on the CLI-supplied ratio, which is parsed via nom::number::complete::float with no range check. Any application embedding imagecli as a library and accepting user-controlled pipeline strings is remotely crashable with a single request.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/70xxx/CVE-2026-70377.json
- https://github.com/theotherphil/imagecli/issues/66
- https://nvd.nist.gov/vuln/detail/CVE-2026-70377
