# [H] OpenStack oslo.messaging does not verify RabbitMQ broker hostname during TLS handshake

## Summary
Severity: High
Advisory: GHSA-76qh-xr7q-h39m
CVE: CVE-2026-44393
CWE: CWE-295, CWE-297
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-76qh-xr7q-h39m
Type: github-advisory

## Affected
- PyPI: `oslo.messaging` — affected >=1.0.0

## Details
An issue was discovered in OpenStack oslo.messaging 1.0.0 through 17.3.0. The oslo.messaging RabbitMQ driver does not perform TLS hostname verification when connecting to the message broker. When ssl_ca_file is configured, the driver enables certificate chain validation but does not pass the expected broker hostname into the underlying TLS stack. Any certificate signed by the deployment CA is accepted regardless of hostname, allowing an attacker who can intercept control-plane traffic to impersonate the RabbitMQ broker and perform a man-in-the-middle attack on RPC and notification traffic. All OpenStack services using oslo.messaging with RabbitMQ over TLS are affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-44393
- https://access.redhat.com/security/cve/CVE-2026-44393
- https://bugs.launchpad.net/oslo.messaging/+bug/2150316
- https://bugzilla.redhat.com/show_bug.cgi?id=2484835
- https://github.com/openstack/oslo.messaging
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-44393.json
- https://wiki.openstack.org/wiki/OSSN/OSSN-0096
