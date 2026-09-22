# [H] mac802154: llsec: reject frames shorter than the authentication tag

## Summary
Severity: High
Advisory: CVE-2026-68125
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68125
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.16.0 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

mac802154: llsec: reject frames shorter than the authentication tag

llsec_do_decrypt_auth() computes the associated-data length for the
AEAD request as

	assoclen += datalen - authlen;

where datalen is the number of bytes after the MAC header and authlen
(4, 8 or 16) is the length of the authentication tag. Nothing verifies
that the frame actually carries at least authlen payload bytes. A
secured frame whose payload is shorter than the tag makes
datalen - authlen negative; assoclen is then passed to
aead_request_set_ad() as an unsigned value close to 4 GiB, so
crypto_aead_decrypt() walks far off the end of the scatterlist that
only spans the real frame.

The frame is fully attacker-controlled and reaches this path from any
IEEE 802.15.4 peer in radio range. Reject frames whose payload is
shorter than the authentication tag before the subtraction.

Dynamically reproduced on a KASAN kernel as a general-protection-fault
in the AEAD scatterwalk, and the fix confirmed.

## References
- https://git.kernel.org/stable/c/2d6b42a61373144298070668fddf06efe79cf2ff
- https://git.kernel.org/stable/c/5bbf0cd9b6a7076af86c75e87e180099be2e11ae
- https://git.kernel.org/stable/c/de80808f37d99c6dc67bb6f97eea00c8f57a8821
- https://git.kernel.org/stable/c/e09e0301d616c1ef38a5e64e8e4326fd39df13cc
- https://git.kernel.org/stable/c/ec7e62d77193131227df49d654d118fdf5a59892
- https://git.kernel.org/stable/c/f20dedce0429b293d4bad604e0d3f65d8ac96c83
- https://git.kernel.org/stable/c/f27ce82eb04960465df71634b196a48a4ecafd50
- https://git.kernel.org/stable/c/fd3a3f28ed60c6af4b2a39933b151d6b27842c3b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68125.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
