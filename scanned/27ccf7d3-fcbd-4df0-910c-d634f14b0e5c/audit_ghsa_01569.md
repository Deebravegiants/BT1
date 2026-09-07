# [H] Command Injection in git-tags-remote

## Summary
Severity: High
Advisory: GHSA-gm9x-q798-hmr4
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-07-29
Source: https://github.com/advisories/GHSA-gm9x-q798-hmr4
Type: github-advisory

## Affected
- npm: `git-tags-remote` — affected >=0 <1.0.4

## Details
All versions of `git-tags-remote ` are vulnerable to Command Injection. The package fails to sanitize the repository input and passes it directly to an `exec` call on the `get` function . This may allow attackers to execute arbitrary code in the system if the `repo` value passed to the function is user-controlled.  

The following proof-of-concept creates a file in `/tmp`:  
```
const gitTagsRemote = require('git-tags-remote');

gitTagsRemote.get('https://github.com/sh0ji/git-tags-remote.git; echo "Injection Success" > /tmp/command-injection.test')
.then(tags => console.log(tags));
```

## References
- https://github.com/sh0ji/git-tags-remote/issues/58
- https://github.com/sh0ji/git-tags-remote/commit/a20488960cbd2c98455386108253094897ebfc1c
- https://github.com/sh0ji/git-tags-remote
- https://www.npmjs.com/advisories/1517
