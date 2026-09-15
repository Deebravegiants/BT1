# [H] Apache Solr: Backup/Restore APIs allow for  deployment of executables in malicious ConfigSets 

## Summary
Severity: High
Advisory: GHSA-37vr-vmg4-jwpw
CVE: CVE-2023-50386
CWE: CWE-434
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-09
Source: https://github.com/advisories/GHSA-37vr-vmg4-jwpw
Type: github-advisory

## Affected
- Maven: `org.apache.solr:solr-core` — affected >=6.0.0 <8.11.3
- Maven: `org.apache.solr:solr-core` — affected >=9.0.0 <9.4.1

## Details
Improper Control of Dynamically-Managed Code Resources, Unrestricted Upload of File with Dangerous Type, Inclusion of Functionality from Untrusted Control Sphere vulnerability in Apache Solr.This issue affects Apache Solr from 6.0.0 through 8.11.2, from 9.0.0 before 9.4.1.

In the affected versions, Solr ConfigSets accepted Java jar and class files to be uploaded through the ConfigSets API.
When backing up Solr Collections, these configSet files would be saved to disk when using the LocalFileSystemRepository (the default for backups).
If the backup was saved to a directory that Solr uses in its ClassPath/ClassLoaders, then the jar and class files would be available to use with any ConfigSet, trusted or untrusted.

When Solr is run in a secure way (Authorization enabled), as is strongly suggested, this vulnerability is limited to extending the Backup permissions with the ability to add libraries.
Users are recommended to upgrade to version 8.11.3 or 9.4.1, which fix the issue.
In these versions, the following protections have been added:

  *  Users are no longer able to upload files to a configSet that could be executed via a Java ClassLoader.
  *  The Backup API restricts saving backups to directories that are used in the ClassLoader.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-50386
- https://github.com/apache/lucene-solr/commit/6c8f24eb9e3fe1cb19058173f2e221de3febfeda
- https://github.com/apache/lucene-solr/commit/7e9a2e67f812032a049836c3aa0b18bf5cd717f9
- https://github.com/apache/solr/commit/644dd3a6d6780d71030f7070754d2f3adce22859
- https://github.com/apache/solr/commit/c79011e81dada2f9bc4b4df32ffb32152ef81152
- https://issues.apache.org/jira/browse/SOLR-16949
- https://solr.apache.org/security.html#cve-2023-50386-apache-solr-backuprestore-apis-allow-for-deployment-of-executables-in-malicious-configsets
- http://www.openwall.com/lists/oss-security/2024/02/09/1
