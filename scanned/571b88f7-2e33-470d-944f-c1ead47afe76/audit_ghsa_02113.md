# [H] Prototype pollution in JointJS

## Summary
Severity: High
Advisory: GHSA-qwp9-52h8-xgg8
CVE: CVE-2020-28480
CWE: CWE-400
Ecosystem: npm
Published: 2021-01-20
Source: https://github.com/advisories/GHSA-qwp9-52h8-xgg8
Type: github-advisory

## Affected
- npm: `jointjs` — affected >=0 <3.3.0

## Details
The package jointjs before 3.3.0 are vulnerable to Prototype Pollution via util.setByPath (https://resources.jointjs.com/docs/jointjs/v3.2/joint.htmlutil.setByPath). The path used the access the object's key and set the value is not properly sanitized, leading to a Prototype Pollution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-28480
- https://github.com/clientIO/joint/pull/1406
- https://github.com/clientIO/joint/blob/master/src/util/util.mjs%23L150
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSBOWER-1062037
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-1062036
- https://snyk.io/vuln/SNYK-JS-JOINTJS-1024444
