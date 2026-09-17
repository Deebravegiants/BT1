# [C] CVE-2022-43404

## Summary
Severity: Critical
Advisory: CVE-2022-43404
Aliases: GHSA-27rf-8mjp-r363
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-10-19
Source: https://osv.dev/vulnerability/CVE-2022-43404
Type: osv

## Details
A sandbox bypass vulnerability involving crafted constructor bodies and calls to sandbox-generated synthetic constructors in Jenkins Script Security Plugin 1183.v774b_0b_0a_a_451 and earlier allows attackers with permission to define and run sandboxed scripts, including Pipelines, to bypass the sandbox protection and execute arbitrary code in the context of the Jenkins controller JVM.

## References
- http://www.openwall.com/lists/oss-security/2022/10/19/3
- https://www.jenkins.io/security/advisory/2022-10-19/#SECURITY-2824%20%281%29
