# [M] CVE-2023-52160

## Summary
Severity: Medium
Advisory: CVE-2023-52160
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2024-02-22
Source: https://osv.dev/vulnerability/CVE-2023-52160
Type: osv

## Details
The implementation of PEAP in wpa_supplicant through 2.10 allows authentication bypass. For a successful attack, wpa_supplicant must be configured to not verify the network's TLS certificate during Phase 1 authentication, and an eap_peap_decrypt vulnerability can then be abused to skip Phase 2 authentication. The attack vector is sending an EAP-TLV Success packet instead of starting Phase 2. This allows an adversary to impersonate Enterprise Wi-Fi networks.

## References
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/N46C4DTVUWK336OYDA4LGALSC5VVPTCC/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QU6IR4KV3ZXJZLK2BY7HAHGZNCP7FPNI/
- https://w1.fi/cgit/hostap/commit/?id=8e6485a1bcb0baffdea9e55255a81270b768439c
- https://www.top10vpn.com/research/wifi-vulnerabilities/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52160.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/N46C4DTVUWK336OYDA4LGALSC5VVPTCC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QU6IR4KV3ZXJZLK2BY7HAHGZNCP7FPNI/
- https://nvd.nist.gov/vuln/detail/CVE-2023-52160
- https://lists.debian.org/debian-lts-announce/2024/02/msg00013.html
