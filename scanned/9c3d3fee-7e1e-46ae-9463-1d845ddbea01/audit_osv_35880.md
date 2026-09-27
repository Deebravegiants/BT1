# [C] CVE-2026-15976

## Summary
Severity: Critical
Advisory: CVE-2026-15976
Aliases: GHSA-wf98-gv64-5wrf
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-15976
Type: osv

## Details
SGLang contains a RCE vulnerability when attempting to load model weights from a HuggingFace repository, specifically within the /update_weights_from_disk, where torch.load(..., weights_only=False) fallback enables pickle deserialization of .bin files.

## References
- https://thoughts.apoorvdayal.com/posts/sglang-disclosures/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15976.json
- https://github.com/sgl-project/sglang/security/advisories/GHSA-wf98-gv64-5wrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-15976
