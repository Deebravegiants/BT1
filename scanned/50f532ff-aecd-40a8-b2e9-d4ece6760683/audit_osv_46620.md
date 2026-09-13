# [H] CVE-2014-3153

## Summary
Severity: High
Advisory: CVE-2014-3153
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2014-06-07
Source: https://osv.dev/vulnerability/CVE-2014-3153
Type: osv

## Details
The futex_requeue function in kernel/futex.c in the Linux kernel through 3.14.5 does not ensure that calls have two different futex addresses, which allows local users to gain privileges via a crafted FUTEX_REQUEUE command that facilitates unsafe waiter modification.

## References
- http://linux.oracle.com/errata/ELSA-2014-0771.html
- http://linux.oracle.com/errata/ELSA-2014-3037.html
- http://linux.oracle.com/errata/ELSA-2014-3038.html
- http://linux.oracle.com/errata/ELSA-2014-3039.html
- http://lists.opensuse.org/opensuse-security-announce/2014-06/msg00014.html
- http://lists.opensuse.org/opensuse-security-announce/2014-06/msg00018.html
- http://lists.opensuse.org/opensuse-security-announce/2014-06/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2014-07/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2014-10/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2014-10/msg00007.html
- http://rhn.redhat.com/errata/RHSA-2014-0800.html
- http://secunia.com/advisories/58500
- http://secunia.com/advisories/58990
- http://secunia.com/advisories/59029
- http://secunia.com/advisories/59092
- http://secunia.com/advisories/59153
- http://secunia.com/advisories/59262
- http://secunia.com/advisories/59309
- http://secunia.com/advisories/59386
- http://secunia.com/advisories/59599
