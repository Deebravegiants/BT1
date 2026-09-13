# [H] Regular Expression Denial of Service (ReDoS) in Prism

## Summary
Severity: High
Advisory: GHSA-gj77-59wh-66hg
CVE: CVE-2021-32723
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2021-06-28
Source: https://github.com/advisories/GHSA-gj77-59wh-66hg
Type: github-advisory

## Affected
- npm: `prismjs` — affected >=0 <1.24.0

## Details
Some languages before 1.24.0 are vulnerable to Regular Expression Denial of Service (ReDoS).

### Impact

When Prism is used to highlight untrusted (user-given) text, an attacker can craft a string that will take a very very long time to highlight. Do not use the following languages to highlight untrusted text.

- ASCIIDoc
- ERB

Other languages are __not__ affected and can be used to highlight untrusted text.

### Patches
This problem has been fixed in Prism v1.24.

### References

- PrismJS/prism#2774
- PrismJS/prism#2688

## References
- https://github.com/PrismJS/prism/security/advisories/GHSA-gj77-59wh-66hg
- https://nvd.nist.gov/vuln/detail/CVE-2021-32723
- https://github.com/PrismJS/prism/pull/2688
- https://github.com/PrismJS/prism/pull/2774
- https://github.com/PrismJS/prism/commit/d85e30da6755fdbe7f8559f8e75d122297167018
- https://github.com/PrismJS/prism
- https://www.oracle.com/security-alerts/cpujan2022.html
