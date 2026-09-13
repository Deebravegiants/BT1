# [C] CVE-2017-17790

## Summary
Severity: Critical
Advisory: CVE-2017-17790
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-12-20
Source: https://osv.dev/vulnerability/CVE-2017-17790
Type: osv

## Details
The lazy_initialize function in lib/resolv.rb in Ruby through 2.4.3 uses Kernel#open, which might allow Command Injection attacks, as demonstrated by a Resolv::Hosts::new argument beginning with a '|' character, a different vulnerability than CVE-2017-17405. NOTE: situations with untrusted input may be highly unlikely.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00024.html
- https://lists.debian.org/debian-lts-announce/2017/12/msg00025.html
- https://lists.debian.org/debian-lts-announce/2018/07/msg00012.html
- https://access.redhat.com/errata/RHSA-2018:0378
- https://access.redhat.com/errata/RHSA-2018:0583
- https://access.redhat.com/errata/RHSA-2018:0584
- https://access.redhat.com/errata/RHSA-2018:0585
- https://www.debian.org/security/2018/dsa-4259
- https://github.com/ruby/ruby/pull/1777
