# [H] wifi: brcmfmac: cyw: fix heap overflow on a short auth frame

## Summary
Severity: High
Advisory: CVE-2026-72003
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72003
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.16.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: brcmfmac: cyw: fix heap overflow on a short auth frame

brcmf_notify_auth_frame_rx() takes the frame length from the firmware
event and copies the frame body with the management header offset
subtracted:

	u32 mgmt_frame_len = e->datalen - sizeof(struct brcmf_rx_mgmt_data);
	...
	memcpy(&mgmt_frame->u, frame,
	       mgmt_frame_len - offsetof(struct ieee80211_mgmt, u));

The only length check is e->datalen >= sizeof(*rxframe), so mgmt_frame_len
can be anything from 0 up. offsetof(struct ieee80211_mgmt, u) is 24. When
mgmt_frame_len is below that, the subtraction wraps as an unsigned value to
a huge length. The memcpy then runs far past the kzalloc'd buffer. A
malicious or malfunctioning AP can make the frame short during the
external SAE auth exchange, so this is a remotely triggered heap overflow.

Reject frames shorter than the management header offset before the copy.

## References
- https://git.kernel.org/stable/c/185bb156c427d0f865d344a6d0eaa02c6d05cc57
- https://git.kernel.org/stable/c/240c8d2c717b3f8153e7e877b22a82518d78dbdc
- https://git.kernel.org/stable/c/55b26abb1fa1ec406b3ad11b43c49c7624257565
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72003.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72003
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
