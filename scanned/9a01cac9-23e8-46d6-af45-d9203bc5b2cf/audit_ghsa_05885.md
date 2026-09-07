# [M] Apache Camel-Azure-Storage-DataLake: the downloadToFile operation built the local download target from the remote path name without constraining it to the configured fileDir

## Summary
Severity: Medium
Advisory: GHSA-7jwc-q3fj-c9pq
CVE: CVE-2026-60093
CWE: CWE-23
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-08-24
Source: https://github.com/advisories/GHSA-7jwc-q3fj-c9pq
Type: github-advisory

## Affected
- Maven: `org.apache.camel:camel-azure-storage-datalake` — affected >=4.0.0 <4.14.9
- Maven: `org.apache.camel:camel-azure-storage-datalake` — affected >=4.15.0 <4.18.4
- Maven: `org.apache.camel:camel-azure-storage-datalake` — affected >=4.19.0 <4.22.0

## Details
Relative path traversal vulnerability in Apache Camel Azure-Storage Datalake component

This issue affects Apache Camel: from 4.0.0 before 4.14.9, from 4.15.0 before 4.18.4, from 4.19.0 before 4.22.0.

The camel-azure-storage-datalake component can download an Azure Data Lake Storage Gen2 file to the local filesystem through its downloadToFile operation, writing into the directory named by the fileDir endpoint option. DataLakeFileOperations.downloadToFile built the local target by joining fileDir with the remote path name exactly as the Azure SDK reported it (new File(fileDir, fileClientWrapper.getFileName())) and passed the result straight to the SDK download call, with no lexical normalization and no check that the resolved location stayed inside fileDir. The remote name is not route-controlled data: the consumer enumerates the filesystem in DataLakeConsumer.createBatchExchangesFromPath, which lists paths and creates one exchange per entry from PathItem.getName() verbatim, applying no name filtering by default. A path name containing parent-directory segments therefore resolved to a location outside the configured fileDir, letting anyone able to influence the names present in the consumed Data Lake filesystem cause Camel to create or overwrite a file at a location of their choosing, with the privileges of the Camel process. Depending on what the process can write to, overwriting a file outside the download directory can escalate beyond the loss of integrity of that file. The fileDir option is an ordinary common-group configuration parameter and carries no security marker, so nothing signalled to users that its value was not being enforced as a containment boundary. Camel's other file-download consumers - camel-file, camel-ftp, camel-smb, camel-mina-sftp and camel-azure-files - already constrained their local downloads to the configured directory using a path-segment boundary check; the camel-azure-storage-datalake download path was not covered by that work.

Users are recommended to upgrade to version 4.22.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.9. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.4. For deployments that cannot upgrade immediately, constrain the names the consumer will act on using the regex endpoint option, which is applied to each listed path name as a full-string match, so that only simple single-segment names are accepted and any name carrying a path separator or a parent-directory segment is filtered out before an exchange is created. Alternatively, avoid the downloadToFile operation on untrusted filesystems and write the payload from the route under a file name the route itself controls, rather than one taken from the remote listing. As defence in depth, treat the object names in any externally writable Data Lake filesystem as untrusted input and do not derive local filesystem paths from them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-60093
- https://github.com/apache/camel/pull/24542
- https://github.com/apache/camel/pull/24581
- https://github.com/apache/camel/pull/24582
- https://github.com/apache/camel/pull/24585
- https://github.com/apache/camel/commit/007929bb732a8c5e3e49d4d3c6c8adc2aab13340
- https://github.com/apache/camel/commit/55fcbaf8bc1936cae90abdea5adecbc43e57340e
- https://github.com/apache/camel/commit/857d0cd3024b706ce80f3d2a4aa111e5e94a3e59
- https://camel.apache.org/security/CVE-2026-60093.html
- https://github.com/apache/camel
- https://github.com/apache/camel/releases/tag/camel-4.14.9
- https://github.com/apache/camel/releases/tag/camel-4.18.4
- https://github.com/apache/camel/releases/tag/camel-4.22.0
- https://issues.apache.org/jira/browse/CAMEL-23942
- http://www.openwall.com/lists/oss-security/2026/08/24/8
