# [C] Azure IoT Platform Device SDK Double Free Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2024-27099
Aliases: GHSA-6rh4-fj44-v4jj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-27
Source: https://osv.dev/vulnerability/CVE-2024-27099
Type: osv

## Details
The uAMQP is a C library for AMQP 1.0 communication to Azure Cloud Services. When processing an incorrect `AMQP_VALUE` failed state, may cause a double free problem. This may cause a RCE. Update submodule with commit 2ca42b6e4e098af2d17e487814a91d05f6ae4987.

## References
- https://github.com/Azure/azure-uamqp-c/security/advisories/GHSA-6rh4-fj44-v4jj
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27099.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27099
- https://github.com/Azure/azure-uamqp-c/commit/2ca42b6e4e098af2d17e487814a91d05f6ae4987
