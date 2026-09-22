# [M] Apache MINA SSHD information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-mjmq-gwgm-5qhm
CVE: CVE-2023-35887
CWE: CWE-200, CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-07-10
Source: https://github.com/advisories/GHSA-mjmq-gwgm-5qhm
Type: github-advisory

## Affected
- Maven: `org.apache.sshd:sshd-common` — affected >=2.1.0 <2.9.3
- Maven: `org.apache.sshd:sshd-sftp` — affected >=1.0.0 <2.9.3
- Maven: `org.apache.sshd:sshd-core` — affected >=1.0.0 <2.1.0

## Details
Exposure of Sensitive Information to an Unauthorized Actor vulnerability in Apache Software Foundation Apache MINA.

In SFTP servers implemented using Apache MINA SSHD that use a RootedFileSystem, logged users may be able to discover "exists/does not exist" information about items outside the rooted tree via paths including parent navigation ("..") beyond the root, or involving symlinks.

This issue affects Apache MINA: from 1.0 before 2.9.3 Users are recommended to upgrade to 2.9.3

Until version 2.1.0, some of the code affected by this vulnerability appeared in org.apache.sshd:sshd-core. Version 2.1.0 contains a [commit](https://github.com/apache/mina-sshd/commit/10de190e7d3f9189deb76b8d08c72334a1fe2df0) where the code was moved to the package org.apache.sshd:sshd-common, which did not exist until version 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-35887
- https://github.com/apache/mina-sshd/pull/362
- https://github.com/apache/mina-sshd/commit/10de190e7d3f9189deb76b8d08c72334a1fe2df0
- https://github.com/apache/mina-sshd/commit/a61e93035f06bff8fc622ad94870fb773d48b9f0
- https://github.com/apache/mina-sshd/commit/c20739b43aab0f7bf2ccad982a6cb37b9d5a8a0b
- https://github.com/apache/mina-sshd
- https://issues.apache.org/jira/browse/SSHD-1324
- https://lists.apache.org/thread/b9qgtqvhnvgfpn0w1gz918p21p53tqk2
