# [C] Icinga 2 has a TLS Certificate Validation Bypass for JSON-RPC and HTTP API Connections

## Summary
Severity: Critical
Advisory: CVE-2024-49369
Aliases: GHSA-j7wq-r9mg-9wpv
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-12
Source: https://osv.dev/vulnerability/CVE-2024-49369
Type: osv

## Details
Icinga is a monitoring system which checks the availability of network resources, notifies users of outages, and generates performance data for reporting. The TLS certificate validation in all Icinga 2 versions starting from 2.4.0 was flawed, allowing an attacker to impersonate both trusted cluster nodes as well as any API users that use TLS client certificates for authentication (ApiUser objects with the client_cn attribute set). This vulnerability has been fixed in v2.14.3, v2.13.10, v2.12.11, and v2.11.12.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49369.json
- https://github.com/Icinga/icinga2/security/advisories/GHSA-j7wq-r9mg-9wpv
- https://nvd.nist.gov/vuln/detail/CVE-2024-49369
- https://github.com/Icinga/icinga2/commit/0419a2c36de408e9a703aec0962061ec9a285d3c
- https://github.com/Icinga/icinga2/commit/2febc5e18ae0c93d989e64ebc2a9fd90e7205ad8
- https://github.com/Icinga/icinga2/commit/3504fc7ed688c10d86988e2029a65efc311393fe
- https://github.com/Icinga/icinga2/commit/869a7d6f0fe38c748e67bacc1fbdd42c933030f6
- https://github.com/Icinga/icinga2/commit/8fed6608912c752b337d977f730547875a820831
- https://icinga.com/blog/2024/11/12/critical-icinga-2-security-releases-2-14-3
