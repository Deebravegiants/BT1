# [H] CSRF vulnerability in Jenkins Libvirt Agents Plugin

## Summary
Severity: High
Advisory: GHSA-mm5c-7mpr-99fm
CVE: CVE-2021-21627
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-mm5c-7mpr-99fm
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:libvirt-slave` — affected >=0 <1.9.1

## Details
Jenkins Libvirt Agents Plugin 1.9.0 and earlier does not require POST requests for a form submission endpoint, resulting in a cross-site request forgery (CSRF) vulnerability.

This vulnerability allows attackers to stop hypervisor domains.

Jenkins Libvirt Agents Plugin 1.9.1 requires POST requests for the affected HTTP endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21627
- https://github.com/jenkinsci/libvirt-slave-plugin/commit/655eab9bde26e8b8e11034f6c405af374564cae7
- https://github.com/jenkinsci/libvirt-slave-plugin
- https://www.jenkins.io/security/advisory/2021-03-18/#SECURITY-1764
- http://www.openwall.com/lists/oss-security/2021/03/18/5
