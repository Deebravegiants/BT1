# [M] CVE-2026-50735

## Summary
Severity: Medium
Advisory: CVE-2026-50735
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/CVE-2026-50735
Type: osv

## Details
pglogical's apply worker does not sufficiently validate the length of certain fields in incoming replication protocol messages before copying them, resulting in an out-of-bounds read. A party acting as the publisher for a subscription, for example a non-PostgreSQL endpoint that speaks the pglogical replication protocol, can return crafted messages that cause the subscriber's apply worker to read beyond the bounds of an allocated buffer, disclosing adjacent process memory or crashing the worker. To exploit the issue an attacker must be able to direct a subscription at an endpoint they control. In default installations this requires privileges normally reserved for a superuser, so the issue is most relevant to managed deployments where the ability to create subscriptions has been delegated to non-superuser roles.

## References
- https://www.enterprisedb.com/docs/security/advisories/cve202650735/
