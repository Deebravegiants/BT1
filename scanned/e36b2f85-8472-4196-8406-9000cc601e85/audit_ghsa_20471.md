# [M] Regular expression deinal of service (ReDoS) in is-my-json-valid

## Summary
Severity: Medium
Advisory: GHSA-4hpf-3wq7-5rpr
CVE: CVE-2018-1107
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2022-01-06
Source: https://github.com/advisories/GHSA-4hpf-3wq7-5rpr
Type: github-advisory

## Affected
- npm: `is-my-json-valid` — affected >=2.0.0 <2.17.2
- npm: `is-my-json-valid` — affected >=0 <1.4.1

## Details
It was discovered that the is-my-json-valid JavaScript library used an inefficient regular expression to validate JSON fields defined to have email format. A specially crafted JSON file could cause it to consume an excessive amount of CPU time when validated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1107
- https://github.com/mafintosh/is-my-json-valid/pull/159
- https://github.com/mafintosh/is-my-json-valid/commit/b3051b277f7caa08cd2edc6f74f50aeda65d2976
- https://bugzilla.redhat.com/show_bug.cgi?id=1546357
- https://snyk.io/vuln/npm:is-my-json-valid:20180214
