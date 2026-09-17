# [H] Jenkins Script Security Plugin has sandbox bypass vulnerability involving crafted constructor bodies

## Summary
Severity: High
Advisory: GHSA-v63g-v339-2673
CVE: CVE-2024-34144
CWE: CWE-693
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-v63g-v339-2673
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1336.vf33a

## Details
Jenkins Script Security Plugin provides a sandbox feature that allows low privileged users to define scripts, including Pipelines, that are generally safe to execute. Calls to code defined inside a sandboxed script are intercepted, and various allowlists are checked to determine whether the call is to be allowed.

Multiple sandbox bypass vulnerabilities exist in Script Security Plugin 1335.vf07d9ce377a_e and earlier:

- Crafted constructor bodies that invoke other constructors can be used to construct any subclassable type via implicit casts.

- Sandbox-defined Groovy classes that shadow specific non-sandbox-defined classes can be used to construct any subclassable type.

These vulnerabilities allow attackers with permission to define and run sandboxed scripts, including Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

- These issues are caused by an incomplete fix of [SECURITY-2824](https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2824%20(1)).

Script Security Plugin 1336.vf33a_a_9863911 has additional restrictions and sanity checks to ensure that super constructors cannot be constructed without being intercepted by the sandbox:

- Calls to to other constructors using this are now intercepted by the sandbox.

- Classes in packages that can be shadowed by Groovy-defined classes are no longer ignored by the sandbox when intercepting super constructor calls.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34144
- https://github.com/jenkinsci/script-security-plugin
- https://github.com/jenkinsci/script-security-plugin/releases/tag/1336.vf33a_a_9863911
- https://www.jenkins.io/security/advisory/2024-05-02/#SECURITY-3341
- http://www.openwall.com/lists/oss-security/2024/05/02/3
