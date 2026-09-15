# [H] tty: n_gsm: fix possible out-of-bounds in gsm0_receive()

## Summary
Severity: High
Advisory: CVE-2024-36016
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-29
Source: https://osv.dev/vulnerability/CVE-2024-36016
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.19.316, >=4.20.0 <5.4.278, >=5.5.0 <5.10.219, >=5.11.0 <5.15.161, >=5.16.0 <6.1.93, >=6.2.0 <6.6.33, >=6.7.0 <6.8.12, >=6.9.0 <6.9.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tty: n_gsm: fix possible out-of-bounds in gsm0_receive()

Assuming the following:
- side A configures the n_gsm in basic option mode
- side B sends the header of a basic option mode frame with data length 1
- side A switches to advanced option mode
- side B sends 2 data bytes which exceeds gsm->len
  Reason: gsm->len is not used in advanced option mode.
- side A switches to basic option mode
- side B keeps sending until gsm0_receive() writes past gsm->buf
  Reason: Neither gsm->state nor gsm->len have been reset after
  reconfiguration.

Fix this by changing gsm->count to gsm->len comparison from equal to less
than. Also add upper limit checks against the constant MAX_MRU in
gsm0_receive() and gsm1_receive() to harden against memory corruption of
gsm->len and gsm->mru.

All other checks remain as we still need to limit the data according to the
user configuration and actual payload size.

## References
- https://git.kernel.org/stable/c/0fb736c9931e02dbc7d9a75044c8e1c039e50f04
- https://git.kernel.org/stable/c/46f52c89a7e7d2691b97a9728e4591d071ca8abc
- https://git.kernel.org/stable/c/47388e807f85948eefc403a8a5fdc5b406a65d5a
- https://git.kernel.org/stable/c/4c267110fc110390704cc065edb9817fdd10ff54
- https://git.kernel.org/stable/c/774d83b008eccb1c48c14dc5486e7aa255731350
- https://git.kernel.org/stable/c/9513d4148950b05bc99fa7314dc883cc0e1605e5
- https://git.kernel.org/stable/c/b229bc6c6ea9fe459fc3fa94fd0a27a2f32aca56
- https://git.kernel.org/stable/c/b890d45aaf02b564e6cae2d2a590f9649330857d
- https://git.kernel.org/stable/c/f126ce7305fe88f49cdabc6db4168b9318898ea3
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36016.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36016
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
