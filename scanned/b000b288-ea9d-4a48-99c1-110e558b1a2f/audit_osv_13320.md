# [M] CVE-2018-19212

## Summary
Severity: Medium
Advisory: CVE-2018-19212
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2018-11-12
Source: https://osv.dev/vulnerability/CVE-2018-19212
Type: osv

## Details
In libwebm through 2018-10-03, there is an abort caused by libwebm::Webm2Pes::InitWebmParser() that will lead to a DoS attack.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1644196
