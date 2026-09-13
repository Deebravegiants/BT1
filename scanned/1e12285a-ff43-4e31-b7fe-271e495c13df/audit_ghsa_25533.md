# [H] Untrusted users can modify some Pipeline libraries in Jenkins Pipeline: Deprecated Groovy Libraries Plugin

## Summary
Severity: High
Advisory: GHSA-hh6f-6fp5-gfpv
CVE: CVE-2022-29047
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-04-13
Source: https://github.com/advisories/GHSA-hh6f-6fp5-gfpv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=0 <2.21.3
- Maven: `org.jenkins-ci.plugins.workflow:workflow-cps-global-lib` — affected >=544.vff04fa68714d <566.vd0a

## Details
Multibranch Pipelines by default limit who can change the Pipeline definition from the Jenkinsfile. This is useful for SCMs like GitHub: Jenkins can build content from users without commit access, but who can submit pull requests, without granting them the ability to modify the Pipeline definition. In that case, Jenkins will just use the Pipeline definition in the pull request’s destination branch instead.

In Pipeline: Deprecated Groovy Libraries Plugin 564.ve62a_4eb_b_e039 and earlier the same protection does not apply to uses of the `library` step with a `retriever` argument pointing to a library in the current build’s repository and branch (e.g., `library(…, retriever: legacySCM(scm))`). This allows attackers able to submit pull requests (or equivalent), but not able to commit directly to the configured SCM, to effectively change the Pipeline behavior by changing the library behavior in their pull request, even if the Pipeline is configured to not trust them.

Pipeline: Deprecated Groovy Libraries Plugin 566.vd0a_a_3334a_555 and 2.21.3 aborts library retrieval if the library would be retrieved from the same repository and revision as the current build, and the revision being built is untrusted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-29047
- https://github.com/jenkinsci/workflow-cps-global-lib-plugin/commit/97bf32458e60ad252cfe5e7949bacf04459cee64
- https://github.com/jenkinsci/workflow-cps-global-lib-plugin/commit/bae59b46cb524549d7f346ba73d3161804c97331
- https://www.jenkins.io/security/advisory/2022-04-12/#SECURITY-1951
