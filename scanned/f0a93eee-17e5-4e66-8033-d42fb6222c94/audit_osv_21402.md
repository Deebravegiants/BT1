# [C] CVE-2021-42740

## Summary
Severity: Critical
Advisory: CVE-2021-42740
Aliases: GHSA-g4rg-993r-mgx7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-21
Source: https://osv.dev/vulnerability/CVE-2021-42740
Type: osv

## Details
The shell-quote package before 1.7.3 for Node.js allows command injection. An attacker can inject unescaped shell metacharacters through a regex designed to support Windows drive letters. If the output of this package is passed to a real shell as a quoted argument to a command with exec(), an attacker can inject arbitrary commands. This is because the Windows drive letter regex character class is {A-z] instead of the correct {A-Za-z]. Several shell metacharacters exist in the space between capital letter Z and lower case letter a, such as the backtick character.

## References
- https://github.com/substack/node-shell-quote/blob/master/CHANGELOG.md#173
- https://www.npmjs.com/package/shell-quote
- https://github.com/substack/node-shell-quote/commit/5799416ed454aa4ec9afafc895b4e31760ea1abe
