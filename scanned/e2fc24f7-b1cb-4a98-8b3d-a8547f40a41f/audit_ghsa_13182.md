# [H] plexus-codehaus vulnerable to directory traversal

## Summary
Severity: High
Advisory: GHSA-g6ph-x5wf-g337
CVE: CVE-2022-4244
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-g6ph-x5wf-g337
Type: github-advisory

## Affected
- Maven: `org.codehaus.plexus:plexus-utils` — affected >=0 <3.0.24

## Details
A flaw was found in plexus-codehaus. A directory traversal attack (also known as path traversal) aims to access files and directories stored outside the intended folder. By manipulating files with dot-dot-slash (`../`) sequences and their variations or by using absolute file paths, it may be possible to access arbitrary files and directories stored on the file system, including application source code, configuration, and other critical system files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4244
- https://github.com/codehaus-plexus/plexus-utils/issues/4
- https://github.com/codehaus-plexus/plexus-utils/commit/33a2853df8185b4519b1b8bfae284f03392618ef
- https://access.redhat.com/errata/RHSA-2023:2135
- https://access.redhat.com/errata/RHSA-2023:3906
- https://access.redhat.com/security/cve/CVE-2022-4244
- https://bugzilla.redhat.com/show_bug.cgi?id=2149841
- https://security.snyk.io/vuln/SNYK-JAVA-ORGCODEHAUSPLEXUS-31521
