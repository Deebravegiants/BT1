# [C] Azure IoT Platform Device SDK Remote Code Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-21646
Aliases: GHSA-j29m-p99g-7hpv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-09
Source: https://osv.dev/vulnerability/CVE-2024-21646
Type: osv

## Details
Azure uAMQP is a general purpose C library for AMQP 1.0. The UAMQP library is used by several clients to implement AMQP protocol communication.  When clients using this library receive a crafted binary type data, an integer overflow or wraparound or memory safety issue can occur and may cause remote code execution.  This vulnerability has been patched in release 2024-01-01.

## References
- https://github.com/Azure/azure-uamqp-c/security/advisories/GHSA-j29m-p99g-7hpv
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21646.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21646
- https://github.com/Azure/azure-uamqp-c/commit/12ddb3a31a5a97f55b06fa5d74c59a1d84ad78fe
