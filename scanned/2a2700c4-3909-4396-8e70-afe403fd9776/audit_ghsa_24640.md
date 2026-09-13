# [H] Sandbox bypass vulnerability in Script Security Plugin

## Summary
Severity: High
Advisory: GHSA-gj3q-p8cm-26rm
CVE: CVE-2020-2134
CWE: CWE-693, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gj3q-p8cm-26rm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1.7.1

## Details
Sandbox protection in Script Security Plugin 1.70 and earlier can be circumvented through:
- Crafted constructor calls and bodies (due to an incomplete fix of [SECURITY-582](https://www.jenkins.io/security/advisory/2017-08-07/#super-constructor-calls))
- Crafted method calls on objects that implement `GroovyInterceptable`

This allows attackers able to specify and run sandboxed scripts to execute arbitrary code in the context of the Jenkins controller JVM.

Script Security Plugin 1.71 has additional restrictions and sanity checks to ensure that super constructors cannot be constructed without being intercepted by the sandbox. In addition, it also intercepts method calls on objects that implement `GroovyInterceptable` as calls to `GroovyObject#invokeMethod(String, Object)`, which is on the list of dangerous signatures and should not be approved for use in the sandbox.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2134
- https://github.com/jenkinsci/script-security-plugin/commit/5b1969e0bdf5cde04a165b847144756b28495788
- https://github.com/jenkinsci/script-security-plugin
- https://jenkins.io/security/advisory/2020-03-09/#SECURITY-1754
- http://www.openwall.com/lists/oss-security/2020/03/09/1
