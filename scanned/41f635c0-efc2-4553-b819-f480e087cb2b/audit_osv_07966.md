# [M] CVE-2016-0708

## Summary
Severity: Medium
Advisory: CVE-2016-0708
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-07-11
Source: https://osv.dev/vulnerability/CVE-2016-0708
Type: osv

## Details
Applications deployed to Cloud Foundry, versions v166 through v227, may be vulnerable to a remote disclosure of information, including, but not limited to environment variables and bound service details. For applications to be vulnerable, they must have been staged using automatic buildpack detection, passed through the Java Buildpack detection script, and allow the serving of static content from within the deployed artifact. The default Apache Tomcat configuration in the affected java buildpack versions for some basic web application archive (WAR) packaged applications are vulnerable to this issue.

## References
- https://www.cloudfoundry.org/blog/cve-2016-0708/
