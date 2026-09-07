# [C] Unsafe deserialization in Apache MINA SSHD

## Summary
Severity: Critical
Advisory: GHSA-fhw8-8j55-vwgq
CVE: CVE-2022-45047
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-11-16
Source: https://github.com/advisories/GHSA-fhw8-8j55-vwgq
Type: github-advisory

## Affected
- Maven: `org.apache.sshd:sshd-common` — affected >=0 <2.9.2
- Maven: `org.apache.sshd:sshd-core` — affected >=0 <2.9.2

## Details
Class org.apache.sshd.server.keyprovider.SimpleGeneratorHostKeyProvider in Apache MINA SSHD <= 2.9.1 uses Java deserialization to load a serialized java.security.PrivateKey. The class is one of several implementations that an implementor using Apache MINA SSHD can choose for loading the host keys of an SSH server.

Until version 2.1.0, the code affected by this vulnerability appeared in `org.apache.sshd:sshd-core`. Version 2.1.0 contains a [commit](https://github.com/apache/mina-sshd/commit/10de190e7d3f9189deb76b8d08c72334a1fe2df0) where the code was moved to the package `org.apache.sshd:sshd-common`, which did not exist until version 2.1.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-45047
- https://github.com/apache/mina-sshd/commit/03238d51586f6b3c0bdbb1a23cf16799344d6c32
- https://github.com/apache/mina-sshd/commit/10de190e7d3f9189deb76b8d08c72334a1fe2df0
- https://github.com/apache/mina-sshd/commit/5a8fe830b2a2308a2b24ac8115a391af477f64f5
- https://github.com/apache/mina-sshd
- https://www.mail-archive.com/dev@mina.apache.org/msg39312.html
