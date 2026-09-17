# [H] Insecure Storage of Sensitive Information in Microweber

## Summary
Severity: High
Advisory: GHSA-j8cx-j9j2-f29w
CVE: CVE-2022-0724
CWE: CWE-922
Ecosystem: Packagist
Published: 2022-02-24
Source: https://github.com/advisories/GHSA-j8cx-j9j2-f29w
Type: github-advisory

## Affected
- Packagist: `microweber/microweber` — affected >=0 <1.3

## Details
Microweber prior to version 1.3 does not strip images of EXIF data, exposing information about users' locations, device hardware, and device software.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0724
- https://github.com/microweber/microweber/commit/b592c86d2b927c0cae5b73b87fb541f25e777aa3
- https://github.com/microweber/microweber
- https://huntr.dev/bounties/0cdc4a29-dada-4264-b326-8b65b4f11062
