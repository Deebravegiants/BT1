# [C] Command Injection in bestzip

## Summary
Severity: Critical
Advisory: GHSA-4qqc-mp5f-ccv4
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-02
Source: https://github.com/advisories/GHSA-4qqc-mp5f-ccv4
Type: github-advisory

## Affected
- npm: `bestzip` — affected >=0 <2.1.7

## Details
Versions of `bestzip` prior to 2.1.7 are vulnerable to Command Injection. The package fails to sanitize input rules and passes it directly to an `exec` call on the `zip` function . This may allow attackers to execute arbitrary code in the system as long as the values of `destination` is user-controlled. This only affects users with a native `zip` command available. The following examples demonstrate the issue from the CLI and also programatically:
- `bestzip test.zip 'sourcefile; mkdir folder'`
- `zip({ source: 'sourcefile', destination: './test.zip; mkdir folder' })`

## References
- https://www.npmjs.com/advisories/1554
