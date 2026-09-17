# [H] CVE-2022-0934

## Summary
Severity: High
Advisory: CVE-2022-0934
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-08-29
Source: https://osv.dev/vulnerability/CVE-2022-0934
Type: osv

## Details
A single-byte, non-arbitrary write/use-after-free flaw was found in dnsmasq. This flaw allows an attacker who sends a crafted packet processed by dnsmasq, potentially causing a denial of service.

## References
- https://thekelleys.org.uk/gitweb/?p=dnsmasq.git%3Ba=commit%3Bh=03345ecefeb0d82e3c3a4c28f27c3554f0611b39
- https://lists.debian.org/debian-lts-announce/2024/11/msg00035.html
- https://lists.thekelleys.org.uk/pipermail/dnsmasq-discuss/2022q1/016272.html
- https://access.redhat.com/security/cve/CVE-2022-0934
- https://bugzilla.redhat.com/show_bug.cgi?id=2057075
