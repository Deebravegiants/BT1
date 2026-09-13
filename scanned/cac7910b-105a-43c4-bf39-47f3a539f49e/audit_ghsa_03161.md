# [M] Regular expression denial of service in @absolunet/kafe

## Summary
Severity: Medium
Advisory: GHSA-hgpf-97c5-74fc
CVE: CVE-2020-7761
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-05-10
Source: https://github.com/advisories/GHSA-hgpf-97c5-74fc
Type: github-advisory

## Affected
- npm: `@absolunet/kafe` — affected >=0 <3.2.10

## Details
This affects the package @absolunet/kafe before 3.2.10. It allows cause a denial of service when validating crafted invalid emails.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7761
- https://github.com/absolunet/kafe/commit/c644c798bfcdc1b0bbb1f0ca59e2e2664ff3fdd0%23diff-f0f4b5b19ad46588ae9d7dc1889f681252b0698a4ead3a77b7c7d127ee657857
- https://snyk.io/vuln/SNYK-JS-ABSOLUNETKAFE-1017403
- https://www.npmjs.com/package/@absolunet/kafe
