# [C] OS Command Injection in async-git

## Summary
Severity: Critical
Advisory: GHSA-6c3f-p5wp-34mh
CVE: CVE-2021-3190
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-01-29
Source: https://github.com/advisories/GHSA-6c3f-p5wp-34mh
Type: github-advisory

## Affected
- npm: `async-git` — affected >=0 <1.13.2

## Details
The async-git package before 1.13.2 for Node.js allows OS Command Injection via shell metacharacters, as demonstrated by git.reset and git.tag. This issue may lead to remote code execution if a client of the library calls the vulnerable method with untrusted input. Ensure to sanitize untrusted user input before passing it to one of the vulnerable functions as a workaround or update async-git to version 1.13.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-3190
- https://github.com/omrilotan/async-git/pull/13
- https://github.com/omrilotan/async-git/pull/13/commits/611823bd97dd41e9e8127c38066868ff9dcfa57a
- https://github.com/omrilotan/async-git/pull/13/commits/a5f45f58941006c4cc1699609383b533d9b92c6a
- https://github.com/omrilotan/async-git/pull/14
- https://advisory.checkmarx.net/advisory/CX-2021-4772
- https://github.com/omrilotan/async-git
- https://www.npmjs.com/package/async-git
