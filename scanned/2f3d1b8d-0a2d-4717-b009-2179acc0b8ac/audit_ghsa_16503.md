# [M] kurwov vulnerable to Denial of Service due to improper data sanitization

## Summary
Severity: Medium
Advisory: GHSA-hfrv-h3q8-9jpr
CVE: CVE-2024-34075
CWE: CWE-502
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-hfrv-h3q8-9jpr
Type: github-advisory

## Affected
- npm: `kurwov` — affected >=3.1.0 <3.2.5

## Details
### Summary
An unsafe sanitization of dataset contents on the `MarkovData#getNext` method used in `Markov#generate` and `Markov#choose` allows a maliciously crafted string on the dataset to throw and stop the function from running properly.

### Details
https://github.com/xiboon/kurwov/blob/0d58dfa42135ab40e830e92622857282f980ca89/src/MarkovData.ts#L38-L44

If a string contains a forbidden substring (i.e. `__proto__`) followed by a space character, the second line will access a special property in `MarkovData#finalData` by removing the last character of the string, bypassing the dataset sanitization (as it is supposed to be already sanitized before this function is called).

`data` is then defined as the special function found in its prototype instead of an array.

On the last line, `data` is then indexed by a random number, which is supposed to return a string but returns undefined as it's a function. Calling `endsWith` then throws.

### PoC
https://runkit.com/embed/m6uu40r5ja9b

### Impact
Any dataset can be contaminated with the substring making it unable to properly generate anything in some cases.

## References
- https://github.com/xiboon/kurwov/security/advisories/GHSA-hfrv-h3q8-9jpr
- https://nvd.nist.gov/vuln/detail/CVE-2024-34075
- https://github.com/xiboon/kurwov/commit/85d63e652594f121d6656177d7a3c0d823c976c9
- https://github.com/xiboon/kurwov
- https://github.com/xiboon/kurwov/blob/0d58dfa42135ab40e830e92622857282f980ca89/src/MarkovData.ts#L38-L44
