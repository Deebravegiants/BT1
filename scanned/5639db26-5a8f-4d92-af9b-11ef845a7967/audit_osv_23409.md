# [H] ASoC: max9759: fix underflow in speaker_gain_control_put()

## Summary
Severity: High
Advisory: CVE-2022-48717
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48717
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.17.0 <4.19.228, >=4.20.0 <5.4.178, >=5.5.0 <5.10.99, >=5.11.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: max9759: fix underflow in speaker_gain_control_put()

Check for negative values of "priv->gain" to prevent an out of bounds
access.  The concern is that these might come from the user via:
  -> snd_ctl_elem_write_user()
    -> snd_ctl_elem_write()
      -> kctl->put()

## References
- https://git.kernel.org/stable/c/4c907bcd9dcd233da6707059d777ab389dcbd964
- https://git.kernel.org/stable/c/5a45448ac95b715173edb1cd090ff24b6586d921
- https://git.kernel.org/stable/c/71e60c170105d153e34d01766c1e4db26a4b24cc
- https://git.kernel.org/stable/c/a0f49d12547d45ea8b0f356a96632dd503941c1e
- https://git.kernel.org/stable/c/baead410e5db49e962a67fffc17ac30e44b50b7c
- https://git.kernel.org/stable/c/f114fd6165dfb52520755cc4d1c1dfbd447b88b6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48717.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48717
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
