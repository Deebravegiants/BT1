# [H] wifi: prevent A-MSDU attacks in mesh networks

## Summary
Severity: High
Advisory: CVE-2025-38512
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-08-16
Source: https://osv.dev/vulnerability/CVE-2025-38512
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <6.1.146, >=6.2.0 <6.6.99, >=6.3.0 <6.12.39, >=6.7.0 <6.15.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: prevent A-MSDU attacks in mesh networks

This patch is a mitigation to prevent the A-MSDU spoofing vulnerability
for mesh networks. The initial update to the IEEE 802.11 standard, in
response to the FragAttacks, missed this case (CVE-2025-27558). It can
be considered a variant of CVE-2020-24588 but for mesh networks.

This patch tries to detect if a standard MSDU was turned into an A-MSDU
by an adversary. This is done by parsing a received A-MSDU as a standard
MSDU, calculating the length of the Mesh Control header, and seeing if
the 6 bytes after this header equal the start of an rfc1042 header. If
equal, this is a strong indication of an ongoing attack attempt.

This defense was tested with mac80211_hwsim against a mesh network that
uses an empty Mesh Address Extension field, i.e., when four addresses
are used, and when using a 12-byte Mesh Address Extension field, i.e.,
when six addresses are used. Functionality of normal MSDUs and A-MSDUs
was also tested, and confirmed working, when using both an empty and
12-byte Mesh Address Extension field.

It was also tested with mac80211_hwsim that A-MSDU attacks in non-mesh
networks keep being detected and prevented.

Note that the vulnerability being patched, and the defense being
implemented, was also discussed in the following paper and in the
following IEEE 802.11 presentation:

https://papers.mathyvanhoef.com/wisec2025.pdf
https://mentor.ieee.org/802.11/dcn/25/11-25-0949-00-000m-a-msdu-mesh-spoof-protection.docx

## References
- https://git.kernel.org/stable/c/6e3b09402cc6c3e3474fa548e8adf6897dda05de
- https://git.kernel.org/stable/c/737bb912ebbe4571195c56eba557c4d7315b26fb
- https://git.kernel.org/stable/c/e01851f6e9a665a6011b14714b271d3e6b0b8d32
- https://git.kernel.org/stable/c/e2c8a3c0388aef6bfc4aabfba07bc7dff16eea80
- https://git.kernel.org/stable/c/ec6392061de6681148b63ee6c8744da833498cdd
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38512.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38512
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
