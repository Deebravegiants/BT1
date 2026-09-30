# [C] Jenkins Plugin Installation Manager Tool did not verify plugin downloads

## Summary
Severity: Critical
Advisory: GHSA-m8r4-c7jm-w782
CVE: CVE-2020-2320
CWE: CWE-494
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-m8r4-c7jm-w782
Type: github-advisory

## Affected
- Maven: `io.jenkins.plugin-management:plugin-management-parent-pom` — affected >=0 <2.2.0

## Details
Jenkins Plugin Installation Manager Tool is part of the Jenkins project Docker images. As `jenkins-plugin-cli` it is used to download and install plugins even before Jenkins is running.

Jenkins Plugin Installation Manager Tool 2.1.3 and earlier does not verify plugin downloads. This may allow third parties such as mirror operators to provide crafted plugin downloads.

Jenkins Plugin Installation Manager Tool 2.2.0 confirms that actual checksums of downloaded plugin match the expected checksums.

Docker images of Jenkins 2.269 and 2.263.1 contain Plugin Installation Manager Tool 2.2.0. Users of older Docker images can change the version they use by extending the Jenkins image and update the tool themselves with:

ARG PLUGIN_CLI_URL=https://github.com/jenkinsci/plugin-installation-manager-tool/releases/download/2.2.0/jenkins-plugin-manager-2.2.0.jar
RUN curl -fsSL ${PLUGIN_CLI_URL} -o /usr/lib/jenkins-plugin-manager.jar
Jenkinsfile Runner [1.0-beta-22](https://github.com/jenkinsci/jenkinsfile-runner/releases/tag/1.0-beta-22) Docker images also include Plugin Installation Manager Tool 2.2.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2320
- https://github.com/jenkinsci/plugin-installation-manager-tool/commit/dfc745c3a97a3fea74a3fe2e92d8a4440cbbf867
- https://github.com/jenkinsci/plugin-installation-manager-tool
- https://www.jenkins.io/security/advisory/2020-12-03/#SECURITY-1856
- http://www.openwall.com/lists/oss-security/2020/12/03/2
