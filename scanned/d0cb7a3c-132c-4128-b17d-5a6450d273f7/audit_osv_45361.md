# [M] ImageMagick before 7.1.2-26 contains a policy bypass vulnerability in the APNG encoder and...

## Summary
Severity: Medium
Advisory: JLSEC-2026-1064
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/JLSEC-2026-1064
Type: osv

## Affected
- Julia: `ImageMagick_jll` — affected >=0 <7.1.2028+0

## Details
ImageMagick before 7.1.2-26 contains a policy bypass vulnerability in the APNG encoder and external delegates due to missing validation checks. Attackers can write files to disallowed paths by bypassing configured policy restrictions through the APNG encoding process.

## References
- https://github.com/ImageMagick/ImageMagick/security/advisories/GHSA-v3j6-27vc-7pw2
- https://github.com/advisories/GHSA-26m2-2whw-vfv9
- https://nvd.nist.gov/vuln/detail/CVE-2026-61858
- https://www.vulncheck.com/advisories/imagemagick-before-26-policy-bypass-via-apng-encoder
