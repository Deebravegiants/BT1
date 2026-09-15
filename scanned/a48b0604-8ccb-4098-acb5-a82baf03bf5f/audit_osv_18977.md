# [H] CVE-2020-5410

## Summary
Severity: High
Advisory: CVE-2020-5410
Aliases: GHSA-32xf-jwmv-9hf3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2020-06-02
Source: https://osv.dev/vulnerability/CVE-2020-5410
Type: osv

## Details
Spring Cloud Config, versions 2.2.x prior to 2.2.3, versions 2.1.x prior to 2.1.9, and older unsupported versions allow applications to serve arbitrary configuration files through the spring-cloud-config-server module. A malicious user, or attacker, can send a request using a specially crafted URL that can lead to a directory traversal attack.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2020-5410
- https://tanzu.vmware.com/security/cve-2020-5410
