# [H] CVE-2024-53427

## Summary
Severity: High
Advisory: CVE-2024-53427
Aliases: GHSA-x6c3-qv5r-7q22
CVSS: 8.1 (CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2024-53427
Type: osv

## Details
decNumberCopy in decNumber.c in jq through 1.7.1 does not properly consider that NaN is interpreted as numeric, which has a resultant stack-based buffer overflow and out-of-bounds write, as demonstrated by use of --slurp with subtraction, such as a filter of .-. when the input has a certain form of digit string with NaN (e.g., "1 NaN123" immediately followed by many more digits).

## References
- https://gist.github.com/Ekkosun/a83870ce7f3b7813b9b462a395e8ad92
- https://github.com/jqlang/jq/blob/71c2ab509a8628dbbad4bc7b3f98a64aa90d3297/src/decNumber/decNumber.c#L3375
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53427.json
- https://github.com/jqlang/jq/security/advisories/GHSA-x6c3-qv5r-7q22
- https://nvd.nist.gov/vuln/detail/CVE-2024-53427
- https://github.com/jqlang/jq/issues/3196
- https://github.com/jqlang/jq/issues/3296
