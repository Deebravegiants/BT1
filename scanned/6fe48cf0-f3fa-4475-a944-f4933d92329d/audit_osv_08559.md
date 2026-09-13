# [M] CVE-2016-4417

## Summary
Severity: Medium
Advisory: CVE-2016-4417
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-05-01
Source: https://osv.dev/vulnerability/CVE-2016-4417
Type: osv

## Details
Off-by-one error in epan/dissectors/packet-gsm_abis_oml.c in the GSM A-bis OML dissector in Wireshark 1.12.x before 1.12.10 and 2.x before 2.0.2 allows remote attackers to cause a denial of service (buffer over-read and application crash) via a crafted packet that triggers a 0xff tag value.

## References
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00015.html
- http://lists.opensuse.org/opensuse-updates/2016-03/msg00016.html
- http://www.oracle.com/technetwork/topics/security/bulletinjul2016-3090568.html
- https://www.wireshark.org/security/wnpa-sec-2016-14.html
- https://bugs.wireshark.org/bugzilla/show_bug.cgi?id=11825
