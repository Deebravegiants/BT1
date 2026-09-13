# [C] Potential Command Injection in hubot-scripts

## Summary
Severity: Critical
Advisory: GHSA-hwch-749c-rv63
CVE: CVE-2013-7378
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-08-31
Source: https://github.com/advisories/GHSA-hwch-749c-rv63
Type: github-advisory

## Affected
- npm: `hubot-scripts` — affected >=0 <2.4.5

## Details
Versions 2.4.3 and earlier of hubot-scripts are vulnerable to a command injection vulnerablity in the `hubot-scripts/package/src/scripts/email.coffee` module.


### Mitigating Factors
The email script is not enabled by default, it has to be manually added to hubot's list of loaded scripts.


## Recommendation

Update hubot-scripts to version 2.4.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7378
- https://github.com/github/hubot-scripts/commit/feee5abdb038a229a98969ae443cdb8a61747782
- https://www.npmjs.com/advisories/13
- http://www.openwall.com/lists/oss-security/2014/05/13/1
- http://www.openwall.com/lists/oss-security/2014/05/15/2
