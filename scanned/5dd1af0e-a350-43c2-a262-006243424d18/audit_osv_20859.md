# [H] CVE-2021-37698

## Summary
Severity: High
Advisory: CVE-2021-37698
Aliases: GHSA-cxfm-8j5v-5qr2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-08-19
Source: https://osv.dev/vulnerability/CVE-2021-37698
Type: osv

## Details
Icinga is a monitoring system which checks the availability of network resources, notifies users of outages, and generates performance data for reporting. In versions 2.5.0 through 2.13.0, ElasticsearchWriter, GelfWriter, InfluxdbWriter and Influxdb2Writer do not verify the server's certificate despite a certificate authority being specified. Icinga 2 instances which connect to any of the mentioned time series databases (TSDBs) using TLS over a spoofable infrastructure should immediately upgrade to version 2.13.1, 2.12.6, or 2.11.11 to patch the issue. Such instances should also change the credentials (if any) used by the TSDB writer feature to authenticate against the TSDB. There are no workarounds aside from upgrading.

## References
- https://lists.debian.org/debian-lts-announce/2024/11/msg00010.html
- https://github.com/Icinga/icinga2/releases/tag/v2.11.11
- https://github.com/Icinga/icinga2/releases/tag/v2.12.6
- https://github.com/Icinga/icinga2/releases/tag/v2.13.1
- https://github.com/Icinga/icinga2/security/advisories/GHSA-cxfm-8j5v-5qr2
- https://lists.debian.org/debian-lts-announce/2021/11/msg00010.html
