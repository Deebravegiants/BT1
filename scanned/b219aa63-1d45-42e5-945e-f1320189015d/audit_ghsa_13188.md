# [M] codehaus-plexus vulnerable to XML injection

## Summary
Severity: Medium
Advisory: GHSA-jcwr-x25h-x5fh
CVE: CVE-2022-4245
CWE: CWE-611, CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-09-25
Source: https://github.com/advisories/GHSA-jcwr-x25h-x5fh
Type: github-advisory

## Affected
- Maven: `org.codehaus.plexus:plexus-utils` — affected >=0 <3.0.24

## Details
A flaw was found in codehaus-plexus. The `org.codehaus.plexus.util.xml.XmlWriterUtil#writeComment` fails to sanitize comments for a `-->` sequence. This issue means that text contained in the command string could be interpreted as XML and allow for XML injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-4245
- https://github.com/codehaus-plexus/plexus-utils/issues/3
- https://github.com/codehaus-plexus/plexus-utils/commit/f933e5e78dc2637e485447ed821fe14904f110de
- https://access.redhat.com/errata/RHSA-2023:2135
- https://access.redhat.com/errata/RHSA-2023:3906
- https://access.redhat.com/security/cve/CVE-2022-4245
- https://bugzilla.redhat.com/show_bug.cgi?id=2149843
- https://github.com/codehaus-plexus/plexus-utils
- https://security.snyk.io/vuln/SNYK-JAVA-ORGCODEHAUSPLEXUS-461102
