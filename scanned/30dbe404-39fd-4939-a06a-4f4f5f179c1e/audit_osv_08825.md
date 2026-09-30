# [H] CVE-2016-6271

## Summary
Severity: High
Advisory: CVE-2016-6271
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-01-18
Source: https://osv.dev/vulnerability/CVE-2016-6271
Type: osv

## Details
The Bzrtp library (aka libbzrtp) 1.0.x before 1.0.4 allows man-in-the-middle attackers to conduct spoofing attacks by leveraging a missing HVI check on DHPart2 packet reception.

## References
- http://www.securityfocus.com/bid/95928
- https://github.com/BelledonneCommunications/bzrtp/commit/bbb1e6e2f467ee4bd7b9a8c800e4f07343d7d99b
- https://github.com/gteissier/CVE-2016-6271
