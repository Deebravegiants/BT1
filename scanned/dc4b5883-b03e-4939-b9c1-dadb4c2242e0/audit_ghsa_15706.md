# [H] Apache Pinot: Unauthorized endpoint exposed sensitive information

## Summary
Severity: High
Advisory: GHSA-8gj9-r4hv-3jjw
CVE: CVE-2024-39676
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-24
Source: https://github.com/advisories/GHSA-8gj9-r4hv-3jjw
Type: github-advisory

## Affected
- Maven: `org.apache.pinot:pinot-controller` — affected >=0.1 <1.0.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Pinot.

This issue affects Apache Pinot: from 0.1 before 1.0.0.

Users are recommended to upgrade to version 1.0.0 and configure RBAC, which fixes the issue.

Details: 

When using a request to path `/appconfigs` to the controller, it can lead to the disclosure of sensitive information such as system information (e.g. arch, os version), environment information (e.g. maxHeapSize) and Pinot configurations (e.g. zookeeper path). This issue was addressed by the Role-based Access Control https://docs.pinot.apache.org/operators/tutorials/authentication/basic-auth-access-control , so that `/appConfigs` and all other APIs can be access controlled. Only authorized users have access to it. Note the user needs to add the admin role accordingly to the RBAC guide to control access to this endpoint, and in the future version of Pinot, a default admin role is planned to be added.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39676
- https://docs.pinot.apache.org/operators/tutorials/authentication/basic-auth-access-control
- https://github.com/apache/pinot
- https://lists.apache.org/thread/hsm0b2w8qr0sqy4rj1mfnnw286tslpzc
- http://www.openwall.com/lists/oss-security/2024/07/23/5
