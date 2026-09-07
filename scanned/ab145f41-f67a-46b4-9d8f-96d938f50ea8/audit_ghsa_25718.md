# [H] Jenkins allows Data Insertion and Execution of Code by those with Read and HTTP Access

## Summary
Severity: High
Advisory: GHSA-wr6p-j63r-xqhv
CVE: CVE-2012-4438
CWE: CWE-20
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-23
Source: https://github.com/advisories/GHSA-wr6p-j63r-xqhv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=0 <1.466.2
- Maven: `org.jenkins-ci.main:jenkins-core` — affected >=1.467 <1.482

## Details
Jenkins main before 1.482 and LTS before 1.466.2 allows remote attackers with read access and HTTP access to Jenkins master to insert data and execute arbitrary code.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-4438
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2012-4438
- https://github.com/jenkinsci/jenkins
- https://security-tracker.debian.org/tracker/CVE-2012-4438
- https://www.cloudbees.com/jenkins-security-advisory-2012-09-17
- http://www.openwall.com/lists/oss-security/2012/09/21/2
