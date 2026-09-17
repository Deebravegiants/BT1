# [C] CVE-2016-0761

## Summary
Severity: Critical
Advisory: CVE-2016-0761
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-25
Source: https://osv.dev/vulnerability/CVE-2016-0761
Type: osv

## Details
Cloud Foundry Garden-Linux versions prior to v0.333.0 and Elastic Runtime 1.6.x version prior to 1.6.17 contain a flaw in managing container files during Docker image preparation that could be used to delete, corrupt or overwrite host files and directories, including other container filesystems on the host.

## References
- https://pivotal.io/security/cve-2016-0761
