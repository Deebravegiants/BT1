# [C] CVE-2016-2141

## Summary
Severity: Critical
Advisory: CVE-2016-2141
Aliases: GHSA-rc7h-x6cq-988q
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-06-30
Source: https://osv.dev/vulnerability/CVE-2016-2141
Type: osv

## Details
It was found that JGroups did not require necessary headers for encrypt and auth protocols from new nodes joining the cluster. An attacker could use this flaw to bypass security restrictions, and use this vulnerability to send and receive messages within the cluster, leading to information disclosure, message spoofing, or further possible attacks.

## References
- https://lists.apache.org/thread.html/rb37cc937d4fc026fb56de4b4ec0d054aa4083c1a4edd0d8360c068a0%40%3Cdev.geode.apache.org%3E
- https://lists.apache.org/thread.html/ra18cac97416abc2958db0b107877c31da28d884fa6e70fd89c87384a%40%3Cdev.geode.apache.org%3E
- https://rhn.redhat.com/errata/RHSA-2016-1329.html
- https://rhn.redhat.com/errata/RHSA-2016-1331.html
- http://www.securityfocus.com/bid/91481
- https://access.redhat.com/errata/RHSA-2016:1376
- https://access.redhat.com/errata/RHSA-2016:1434
- https://rhn.redhat.com/errata/RHSA-2016-1330.html
- https://rhn.redhat.com/errata/RHSA-2016-1332.html
- http://rhn.redhat.com/errata/RHSA-2016-1439.html
- http://www.securitytracker.com/id/1036165
- https://access.redhat.com/errata/RHSA-2016:1345
- https://access.redhat.com/errata/RHSA-2016:1374
- https://access.redhat.com/errata/RHSA-2016:1389
- https://rhn.redhat.com/errata/RHSA-2016-1334.html
- https://access.redhat.com/errata/RHSA-2016:1346
- https://access.redhat.com/errata/RHSA-2016:1433
- https://rhn.redhat.com/errata/RHSA-2016-1328.html
- https://rhn.redhat.com/errata/RHSA-2016-1333.html
- http://rhn.redhat.com/errata/RHSA-2016-1435.html
