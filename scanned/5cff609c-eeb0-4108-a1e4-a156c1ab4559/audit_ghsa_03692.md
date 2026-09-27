# [C] Command Injection in open

## Summary
Severity: Critical
Advisory: GHSA-28xh-wpgr-7fm8
CWE: CWE-77
Ecosystem: npm
Published: 2019-06-20
Source: https://github.com/advisories/GHSA-28xh-wpgr-7fm8
Type: github-advisory

## Affected
- npm: `open` — affected >=0 <6.0.0

## Details
Versions of `open` before 6.0.0 are vulnerable to command injection when unsanitized user input is passed in.

The package does come with the following warning in the readme:

```
The same care should be taken when calling open as if you were calling child_process.exec directly. If it is an executable it will run in a new shell.
```


## Recommendation

`open` is now the deprecated `opn` package. Upgrading to the latest version is likely have unwanted effects since it now has a very different API but will prevent this vulnerability.

## References
- https://github.com/pwnall/node-open/issues/68
- https://github.com/pwnall/node-open/issues/69
- https://hackerone.com/reports/319473
- https://www.npmjs.com/advisories/663
