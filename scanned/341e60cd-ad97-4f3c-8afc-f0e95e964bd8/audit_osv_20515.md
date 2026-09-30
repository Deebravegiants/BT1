# [M] CVE-2021-34434

## Summary
Severity: Medium
Advisory: CVE-2021-34434
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2021-08-30
Source: https://osv.dev/vulnerability/CVE-2021-34434
Type: osv

## Details
In Eclipse Mosquitto versions 2.0 to 2.0.11, when using the dynamic security plugin, if the ability for a client to make subscriptions on a topic is revoked when a durable client is offline, then existing subscriptions for that client are not revoked.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K4WWGVF5BUFPYPCFUPPP4KRIYI5OTJN2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/RLUUM52Y6AEICPXPSRRXC6OBY4H5XKW7/
- https://www.debian.org/security/2023/dsa-5511
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=575324
