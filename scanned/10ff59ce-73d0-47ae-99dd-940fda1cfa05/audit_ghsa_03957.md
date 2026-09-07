# [C] Potential Command Injection in shell-quote

## Summary
Severity: Critical
Advisory: GHSA-qg8p-v9q4-gh34
CVE: CVE-2016-10541
CWE: CWE-78, CWE-94
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-02-18
Source: https://github.com/advisories/GHSA-qg8p-v9q4-gh34
Type: github-advisory

## Affected
- npm: `shell-quote` — affected >=0 <1.6.1

## Details
Affected versions of `shell-quote` do not properly escape command line arguments, which may result in command injection if the library is used to escape user input destined for use as command line arguments.



## Proof of Concept:

The following characters are not escaped properly: `>`,`;`,`{`,`}`

Bash has a neat but not well known feature known as "Bash Brace Expansion", wherein a sub-command can be executed without spaces by running it between a set of `{}` and using the `,` instead of ` ` to seperate arguments. Because of this, full command injection is possible even though it was initially thought to be impossible. 

```
   const quote = require('shell-quote').quote;
   console.log(quote(['a;{echo,test,123,234}']));
   // Actual                    "a;{echo,test,123,234}"
   // Expected                  "a\;\{echo,test,123,234\}"
   // Functional Equivalent     "a; echo 'test' '123' '1234'"
```



## Recommendation

Update to version 1.6.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10541
- https://github.com/advisories/GHSA-qg8p-v9q4-gh34
- https://www.npmjs.com/advisories/117
