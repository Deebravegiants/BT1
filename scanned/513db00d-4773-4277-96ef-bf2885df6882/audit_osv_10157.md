# [M] CVE-2017-14114

## Summary
Severity: Medium
Advisory: CVE-2017-14114
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L)
Published: 2017-09-02
Source: https://osv.dev/vulnerability/CVE-2017-14114
Type: osv

## Details
RTPproxy through 2.2.alpha.20160822 has a NAT feature that results in not properly determining the IP address and port number of the legitimate recipient of RTP traffic, which allows remote attackers to obtain sensitive information or cause a denial of service (communication outage) via crafted RTP packets.

## References
- https://rtpbleed.com
