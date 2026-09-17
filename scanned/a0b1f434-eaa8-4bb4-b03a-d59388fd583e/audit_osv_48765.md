# [M] CVE-2018-1279

## Summary
Severity: Medium
Advisory: CVE-2018-1279
CVSS: 6.5 (CVSS:3.0/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-12-10
Source: https://osv.dev/vulnerability/CVE-2018-1279
Type: osv

## Details
Pivotal RabbitMQ for PCF, all versions, uses a deterministically generated cookie that is shared between all machines when configured in a multi-tenant cluster. A remote attacker who can gain information about the network topology can guess this cookie and, if they have access to the right ports on any server in the MQ cluster can use this cookie to gain full control over the entire cluster.

## References
- https://pivotal.io/security/cve-2018-1279
