# [H] Jenkins Script Security Plugin sandbox bypass vulnerability

## Summary
Severity: High
Advisory: GHSA-2g4q-9vm9-9fw4
CVE: CVE-2024-34145
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-02
Source: https://github.com/advisories/GHSA-2g4q-9vm9-9fw4
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:script-security` — affected >=0 <1336.vf33a

## Details
Jenkins Script Security Plugin provides a sandbox feature that allows low privileged users to define scripts, including Pipelines, that are generally safe to execute. Calls to code defined inside a sandboxed script are intercepted, and various allowlists are checked to determine whether the call is to be allowed.

Multiple sandbox bypass vulnerabilities exist in Script Security Plugin 1335.vf07d9ce377a_e and earlier:

- Crafted constructor bodies that invoke other constructors can be used to construct any subclassable type via implicit casts.

- Sandbox-defined Groovy classes that shadow specific non-sandbox-defined classes can be used to construct any subclassable type.

These vulnerabilities allow attackers with permission to define and run sandboxed scripts, including Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34145
- https://www.jenkins.io/security/advisory/2024-05-02/#SECURITY-3341
- http://www.openwall.com/lists/oss-security/2024/05/02/3
