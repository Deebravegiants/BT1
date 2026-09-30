# [H] Removal of functional code in faker.js

## Summary
Severity: High
Advisory: GHSA-5w9c-rv96-fr7g
Ecosystem: npm
Published: 2022-03-22
Source: https://github.com/advisories/GHSA-5w9c-rv96-fr7g
Type: github-advisory

## Affected
- npm: `faker` — affected 6.6.6

## Details
Faker.js helps users create large amounts of data for testing and development. The maintainer deliberately removed the functional code from this package. This appears to be a purposeful and successful attempt to make the package unusable. This is related to the colors.js [CVE-2021-23567](https://github.com/advisories/GHSA-gh88-3pxp-6fm8). 

The functional code for this package was forked and can be found [here](https://github.com/faker-js/faker).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-23567
- https://github.com/Marak/colors.js/issues/285
- https://github.com/Marak/colors.js/issues/285%23issuecomment-1008212640
- https://github.com/Marak/colors.js/commit/074a0f8ed0c31c35d13d28632bd8a049ff136fb6#diff-92bbac9a308cd5fcf9db165841f2d90ce981baddcb2b1e26cfff170929af3bd1R18
- https://github.com/Marak/Faker.js
- https://github.com/advisories/GHSA-gh88-3pxp-6fm8
- https://snyk.io/vuln/SNYK-JS-COLORS-2331906
- https://www.npmjs.com/package/@faker-js/faker
- https://www.npmjs.com/package/faker
