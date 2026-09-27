# [M] Apache StreamPark: maven build params could trigger remote command execution

## Summary
Severity: Medium
Advisory: GHSA-5v69-92vw-fmjh
CVE: CVE-2024-29737
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-5v69-92vw-fmjh
Type: github-advisory

## Affected
- Maven: `org.apache.streampark:streampark` — affected >=0 <2.1.4

## Details
In streampark, the project module integrates Maven's compilation capabilities. The input parameter validation is not strict, allowing attackers to insert commands for remote command execution, The prerequisite for a successful attack is that the user needs to log in to the streampark system and have system-level permissions. Generally, only users of that system have the authorization to log in, and users would not manually input a dangerous operation command. Therefore, the risk level of this vulnerability is very low.

Mitigation:

all users should upgrade to 2.1.4

Background info:

Log in to Streampark using the default username (e.g. test1, test2, test3) and the default password (streampark). Navigate to the Project module, then add a new project. Enter the git repository address of the project and input `touch /tmp/success_2.1.2` as the "Build Argument". Note that there is no verification and interception of the special character "`". As a result, you will find that this injection command will be successfully executed after executing the build.

In the latest version, the special symbol ` is intercepted.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-29737
- https://github.com/apache/streampark
- https://lists.apache.org/thread/xhx7jt1t24s6d7o435wxng8t0ojfbfh5
- http://www.openwall.com/lists/oss-security/2024/07/17/2
