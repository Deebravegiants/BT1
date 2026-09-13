# [M] Secret file credentials stored unencrypted in rare cases by Plain Credentials Plugin 

## Summary
Severity: Medium
Advisory: GHSA-3cpq-rw36-cppv
CVE: CVE-2024-39459
CWE: CWE-319, CWE-922
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-26
Source: https://github.com/advisories/GHSA-3cpq-rw36-cppv
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:plain-credentials` — affected >=0 <183.va

## Details
When creating secret file credentials Plain Credentials Plugin 182.v468b_97b_9dcb_8 and earlier attempts to decrypt the content of the file to check if it constitutes a valid encrypted secret. In rare cases the file content matches the expected format of an encrypted secret, and the file content will be stored unencrypted (only Base64 encoded) on the Jenkins controller file system.

These credentials can be viewed by users with access to the Jenkins controller file system (global credentials) or with Item/Extended Read permission (folder-scoped credentials).

Plain Credentials Plugin 183.va_de8f1dd5a_2b_ no longer attempts to decrypt the content of the file when creating secret file credentials.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39459
- https://github.com/jenkinsci/plain-credentials-plugin/commit/ade8f1dd5a2bc69357995fd50baac56d73f80813
- https://github.com/jenkinsci/plain-credentials-plugin
- https://www.jenkins.io/security/advisory/2024-06-26/#SECURITY-2495
- http://www.openwall.com/lists/oss-security/2024/06/26/2
