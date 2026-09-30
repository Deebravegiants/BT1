# [M] Jenkins directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-v759-3fh9-84mx
CVE: CVE-2014-2059
CWE: CWE-22
Ecosystem: Maven
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-v759-3fh9-84mx
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.533 <1.551
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.532.2

## Details
Directory traversal vulnerability in the CLI job creation (hudson/cli/CreateJobCommand.java) in Jenkins before 1.551 and LTS before 1.532.2 allows remote authenticated users to overwrite arbitrary files via the job name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2059
- https://github.com/jenkinsci/jenkins/commit/ad38d8480f20ce3cbf8fec3e2003bc83efda4f7d
- https://exchange.xforce.ibmcloud.com/vulnerabilities/91346
- https://github.com/jenkinsci/jenkins
- https://wiki.jenkins-ci.org/display/SECURITY/Jenkins+Security+Advisory+2014-02-14
- http://seclists.org/oss-sec/2014/q1/421
