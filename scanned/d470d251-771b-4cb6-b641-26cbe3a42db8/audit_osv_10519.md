# [C] CVE-2017-16820

## Summary
Severity: Critical
Advisory: CVE-2017-16820
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-14
Source: https://osv.dev/vulnerability/CVE-2017-16820
Type: osv

## Details
The csnmp_read_table function in snmp.c in the SNMP plugin in collectd before 5.6.3 is susceptible to a double free in a certain error case, which could lead to a crash (or potentially have other impact).

## References
- https://access.redhat.com/errata/RHSA-2018:0252
- https://access.redhat.com/errata/RHSA-2018:0299
- https://access.redhat.com/errata/RHSA-2018:0560
- https://access.redhat.com/errata/RHSA-2018:1605
- https://access.redhat.com/errata/RHSA-2018:2615
- https://security.gentoo.org/glsa/201803-10
- https://bugs.debian.org/881757
- https://github.com/collectd/collectd/issues/2291
- https://github.com/collectd/collectd/releases/tag/collectd-5.6.3
- https://github.com/collectd/collectd/commit/d16c24542b2f96a194d43a73c2e5778822b9cb47
