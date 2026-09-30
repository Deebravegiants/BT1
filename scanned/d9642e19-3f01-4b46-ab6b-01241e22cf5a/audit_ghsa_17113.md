# [C] Apache Pulsar: Pulsar Functions Worker's Archive Extraction Vulnerability Allows Unauthorized File Modification

## Summary
Severity: Critical
Advisory: GHSA-jg2g-4rjg-cmqh
CVE: CVE-2024-27317
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-03-12
Source: https://github.com/advisories/GHSA-jg2g-4rjg-cmqh
Type: github-advisory

## Affected
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=2.4.0 <2.10.6
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=2.11.0 <2.11.4
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.0.0 <3.0.3
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.1.0 <3.1.3
- Maven: `org.apache.pulsar:pulsar-functions-worker` — affected >=3.2.0 <3.2.1

## Details
In Pulsar Functions Worker, authenticated users can upload functions in jar or nar files. These files, essentially zip files, are extracted by the Functions Worker. However, if a malicious file is uploaded, it could exploit a directory traversal vulnerability. This occurs when the filenames in the zip files, which aren't properly validated, contain special elements like "..", altering the directory path. This could allow an attacker to create or modify files outside of the designated extraction directory, potentially influencing system behavior. This vulnerability also applies to the Pulsar Broker when it is configured with "functionsWorkerEnabled=true".

This issue affects Apache Pulsar versions from 2.4.0 to 2.10.5, from 2.11.0 to 2.11.3, from 3.0.0 to 3.0.2, from 3.1.0 to 3.1.2, and 3.2.0. 

2.10 Pulsar Function Worker users should upgrade to at least 2.10.6.
2.11 Pulsar Function Worker users should upgrade to at least 2.11.4.
3.0 Pulsar Function Worker users should upgrade to at least 3.0.3.
3.1 Pulsar Function Worker users should upgrade to at least 3.1.3.
3.2 Pulsar Function Worker users should upgrade to at least 3.2.1.

Users operating versions prior to those listed above should upgrade to the aforementioned patched versions or newer versions.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-27317
- https://github.com/apache/pulsar
- https://lists.apache.org/thread/ct9xmvlf7lompc1pxvlsb60qstfsm9po
- https://pulsar.apache.org/security/CVE-2024-27317
- http://www.openwall.com/lists/oss-security/2024/03/12/10
