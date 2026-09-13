# [M] CVE-2020-14312

## Summary
Severity: Medium
Advisory: CVE-2020-14312
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2021-02-06
Source: https://osv.dev/vulnerability/CVE-2020-14312
Type: osv

## Details
A flaw was found in the default configuration of dnsmasq, as shipped with Fedora versions prior to 31 and in all versions Red Hat Enterprise Linux, where it listens on any interface and accepts queries from addresses outside of its local subnet. In particular, the option `local-service` is not enabled. Running dnsmasq in this manner may inadvertently make it an open resolver accessible from any address on the internet. This flaw allows an attacker to conduct a Distributed Denial of Service (DDoS) against other systems.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1851342
