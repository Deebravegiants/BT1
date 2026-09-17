# [H] CVE-2019-18934

## Summary
Severity: High
Advisory: CVE-2019-18934
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2019-11-19
Source: https://osv.dev/vulnerability/CVE-2019-18934
Type: osv

## Details
Unbound 1.6.4 through 1.9.4 contain a vulnerability in the ipsec module that can cause shell code execution after receiving a specially crafted answer. This issue can only be triggered if unbound was compiled with `--enable-ipsecmod` support, and ipsecmod is enabled and used in the configuration.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MOCR6JP7MSRARTOGEHGST64G4FJGX5VK/
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00067.html
- http://lists.opensuse.org/opensuse-security-announce/2020-06/msg00069.html
- https://github.com/NLnetLabs/unbound/blob/release-1.9.5/doc/Changelog
- https://www.nlnetlabs.nl/news/2019/Nov/19/unbound-1.9.5-released/
- https://www.nlnetlabs.nl/downloads/unbound/CVE-2019-18934.txt
- http://www.openwall.com/lists/oss-security/2019/11/19/1
