# [H] CVE-2018-1000866

## Summary
Severity: High
Advisory: CVE-2018-1000866
Aliases: GHSA-gqhm-4h93-rrhg
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-1000866
Type: osv

## Details
A sandbox bypass vulnerability exists in Pipeline: Groovy Plugin 2.59 and earlier in groovy-sandbox/src/main/java/org/kohsuke/groovy/sandbox/SandboxTransformer.java, groovy-cps/lib/src/main/java/com/cloudbees/groovy/cps/SandboxCpsTransformer.java that allows attackers with Job/Configure permission, or unauthorized attackers with SCM commit privileges and corresponding pipelines based on Jenkinsfiles set up in Jenkins, to execute arbitrary code on the Jenkins master JVM

## References
- https://access.redhat.com/errata/RHBA-2019:0326
- https://access.redhat.com/errata/RHBA-2019:0327
- https://jenkins.io/security/advisory/2018-10-29/#SECURITY-1186
