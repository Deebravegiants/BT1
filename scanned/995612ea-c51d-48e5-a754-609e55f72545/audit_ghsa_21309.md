# [H] v8n vulnerable to Inefficient Regular Expression Complexity

## Summary
Severity: High
Advisory: GHSA-xrx9-gj26-5wx9
CVE: CVE-2022-35923
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-xrx9-gj26-5wx9
Type: github-advisory

## Affected
- npm: `v8n` — affected >=0 <1.5.1

## Details
### Impact
Inefficient regular expression complexity of `lowercase()` and `uppercase()` regex could lead to a denial of service attack. With a formed payload `'a' + 'a'.repeat(i) + 'A'`, only 32 characters payload could take 29443 ms time execution when testing `lowercase()`. The same issue happens with `uppercase()`.

### Patches
v1.5.1

### References
[huntr.dev report](https://huntr.dev/bounties/2d92f644-593b-43b4-bfd1-c8042ac60609)
[_Regular Expression Denial of Service (ReDoS) and Catastrophic Backtracking_](https://snyk.io/blog/redos-and-catastrophic-backtracking/)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [v8n issues list](https://github.com/imbrn/v8n)
* Email us at [brunodev02221@gmail.com](mailto:brunodev02221@gmail.com)

## References
- https://github.com/imbrn/v8n/security/advisories/GHSA-xrx9-gj26-5wx9
- https://nvd.nist.gov/vuln/detail/CVE-2022-35923
- https://github.com/imbrn/v8n/commit/92393862156fad190c05ec3f6e2bc73308dcd2f9
- https://github.com/imbrn/v8n
- https://huntr.dev/bounties/2d92f644-593b-43b4-bfd1-c8042ac60609
