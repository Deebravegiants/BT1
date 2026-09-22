# [H] Apache Pulsar Function Worker: Incorrect Authorization for Function Worker Can Leak Sink/Source Credentials

## Summary
Severity: High
Advisory: CVE-2023-37579
Aliases: GHSA-74mc-g2xv-pch2
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2023-07-12
Source: https://osv.dev/vulnerability/CVE-2023-37579
Type: osv

## Details
Incorrect Authorization vulnerability in Apache Software Foundation Apache Pulsar Function Worker.

This issue affects Apache Pulsar: before 2.10.4, and 2.11.0.

Any authenticated user can retrieve a source's configuration or a sink's configuration without authorization. Many sources and sinks contain credentials in the configuration, which could lead to leaked credentials. This vulnerability is mitigated by the fact that there is not a known way for an authenticated user to enumerate another tenant's sources or sinks, meaning the source or sink name would need to be guessed in order to exploit this vulnerability.

The recommended mitigation for impacted users is to upgrade the Pulsar Function Worker to a patched version.

2.10 Pulsar Function Worker users should upgrade to at least 2.10.4.
2.11 Pulsar Function Worker users should upgrade to at least 2.11.1.
3.0 Pulsar Function Worker users are unaffected.
Any users running the Pulsar Function Worker for 2.9.* and earlier should upgrade to one of the above patched versions.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37579.json
- https://lists.apache.org/thread/0dmn3cb5n2p08o3cpj3ycfhzfqs2ppwz
- https://nvd.nist.gov/vuln/detail/CVE-2023-37579
