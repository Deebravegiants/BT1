# [M] CVE-2016-0800

## Summary
Severity: Medium
Advisory: CVE-2016-0800
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2016-03-01
Source: https://osv.dev/vulnerability/CVE-2016-0800
Type: osv

## Details
The SSLv2 protocol, as used in OpenSSL before 1.0.1s and 1.0.2 before 1.0.2g and other products, requires a server to send a ServerVerify message before establishing that a client possesses certain plaintext RSA data, which makes it easier for remote attackers to decrypt TLS ciphertext data by leveraging a Bleichenbacher RSA padding oracle, aka a "DROWN" attack.

## References
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10722
- http://kb.juniper.net/InfoCenter/index?page=content&id=JSA10759
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00001.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00002.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00003.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00004.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00005.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00006.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00007.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00009.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00012.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00017.html
- http://lists.opensuse.org/opensuse-security-announce/2016-03/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2016-04/msg00038.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2016-05/msg00017.html
- http://marc.info/?l=bugtraq&m=145983526810210&w=2
- http://marc.info/?l=bugtraq&m=146108058503441&w=2
