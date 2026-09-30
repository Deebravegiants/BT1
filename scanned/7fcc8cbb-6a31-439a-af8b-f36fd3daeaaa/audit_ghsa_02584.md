# [H] Inefficient Regular Expression Complexity in vuelidate

## Summary
Severity: High
Advisory: GHSA-vvf2-ppj9-pp49
CVE: CVE-2021-3794
CWE: CWE-1333, CWE-400, CWE-697
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-vvf2-ppj9-pp49
Type: github-advisory

## Affected
- npm: `@vuelidate/validators` — affected >=0 <2.0.0-alpha.22

## Details
vuelidate is a simple, lightweight model-based validation for Vue.js 2.x & 3.0. A ReDoS (regular expression denial of service) flaw was found in the `@vuelidate/validators` package. An attacker that is able to provide crafted input to the url(input) function may cause an application to consume an excessive amount of CPU.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3794
- https://github.com/vuelidate/vuelidate/commit/1f0ca31c30e5032f00dbd14c4791b5ee7928f71d
- https://github.com/vuelidate/vuelidate
- https://huntr.dev/bounties/d8201b98-fb91-4c12-a6f7-181b4a20d9b7
