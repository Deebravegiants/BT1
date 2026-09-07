# [H] images vulnerable to Denial of Service

## Summary
Severity: High
Advisory: GHSA-vjpv-x8p9-7p85
CVE: CVE-2024-21523
CWE: CWE-241, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-10
Source: https://github.com/advisories/GHSA-vjpv-x8p9-7p85
Type: github-advisory

## Affected
- npm: `images` — affected >=0

## Details
All versions of the package images are vulnerable to Denial of Service (DoS) due to providing unexpected input types to several different functions. This makes it possible to reach an assert macro, leading to a process crash.

**Note:**
By providing some specific integer values (like 0) to the size function, it is possible to obtain a Segmentation fault error, leading to the process crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21523
- https://gist.github.com/dellalibera/8b4ea6b4db84cba212e6e6e39a6933d1
- https://github.com/zhangyuanwei/node-images
- https://github.com/zhangyuanwei/node-images/blob/691d49f4e620b4eec9f1c47b1735841d9d8b55f6/src/Image.cc
- https://security.snyk.io/vuln/SNYK-JS-IMAGES-6421826
