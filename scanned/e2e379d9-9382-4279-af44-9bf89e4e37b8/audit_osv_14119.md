# [H] CVE-2018-7321

## Summary
Severity: High
Advisory: CVE-2018-7321
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-02-23
Source: https://osv.dev/vulnerability/CVE-2018-7321
Type: osv

## Details
In Wireshark 2.4.0 to 2.4.4 and 2.2.0 to 2.2.12, epan/dissectors/packet-thrift.c had a large loop that was addressed by not proceeding with dissection after encountering an unexpected type.

## References
- https://code.wireshark.org/review/gitweb?p=wireshark.git%3Ba=commit%3Bh=c784d551ad50864de1035ce54e72837301cf6aca
- http://www.securityfocus.com/bid/103158
- https://www.wireshark.org/security/wnpa-sec-2018-06.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=14379
