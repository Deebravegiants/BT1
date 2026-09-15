# [M] sharp vulnerable to Command Injection in post-installation over build environment

## Summary
Severity: Medium
Advisory: GHSA-gp95-ppv5-3jc5
CVE: CVE-2022-29256
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-01
Source: https://github.com/advisories/GHSA-gp95-ppv5-3jc5
Type: github-advisory

## Affected
- npm: `sharp` — affected >=0 <0.30.5

## Details
There's a possible vulnerability in logic that is run only at `npm install` time when installing versions of `sharp` prior to the latest v0.30.5.

This is not part of any runtime code, does not affect Windows users at all, and is unlikely to affect anyone that already cares about the security of their build environment. However, out of an abundance of caution, I've created this advisory.

If an attacker has the ability to set the value of the `PKG_CONFIG_PATH` environment variable in a build environment then they might be able to use this to inject an arbitrary command at `npm install` time.

I've used the Common Vulnerability Scoring System (CVSS) calculator to determine the maximum possible impact, which suggests a "medium" score of 5.9, but for most people the real impact will be dealing with the noise from automated security tooling that this advisory will bring.

[`AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H/E:P/RL:O/RC:C/CR:X/IR:X/AR:X/MAV:X/MAC:X/MPR:X/MUI:R/MS:X/MC:X/MI:X/MA:X`](https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H/E:P/RL:O/RC:C/CR:X/IR:X/AR:X/MAV:X/MAC:X/MPR:X/MUI:R/MS:X/MC:X/MI:X/MA:X&version=3.1)

This problem was fixed in commit a6aeef6 and published as part of `sharp` v0.30.5.

Thank you very much to @dwisiswant0 for the responsible disclosure.

Remember: if an attacker has control over environment variables in your build environment then you have a bigger problem to deal with than this issue.

## References
- https://github.com/lovell/sharp/security/advisories/GHSA-gp95-ppv5-3jc5
- https://nvd.nist.gov/vuln/detail/CVE-2022-29256
- https://github.com/lovell/sharp/commit/a6aeef612be50f5868a77481848b1de674216f0c
- https://advisory.dw1.io/54
- https://github.com/lovell/sharp
