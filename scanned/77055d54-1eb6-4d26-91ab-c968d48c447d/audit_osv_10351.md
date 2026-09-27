# [H] CVE-2017-15089

## Summary
Severity: High
Advisory: CVE-2017-15089
Aliases: GHSA-46r5-59fg-2fjc
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-15
Source: https://osv.dev/vulnerability/CVE-2017-15089
Type: osv

## Details
It was found that the Hotrod client in Infinispan before 9.2.0.CR1 would unsafely read deserialized data on information from the cache. An authenticated attacker could inject a malicious object into the data cache and attain deserialization on the client, and possibly conduct further attacks.

## References
- http://www.securitytracker.com/id/1040360
- https://access.redhat.com/errata/RHSA-2018:0294
- https://access.redhat.com/errata/RHSA-2018:0478
- https://access.redhat.com/errata/RHSA-2018:0479
- https://access.redhat.com/errata/RHSA-2018:0480
- https://access.redhat.com/errata/RHSA-2018:0481
- https://access.redhat.com/errata/RHSA-2018:0501
- https://access.redhat.com/errata/RHSA-2019:1326
- https://github.com/infinispan/infinispan/pull/5639
