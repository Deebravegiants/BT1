# [M] ALSA: jack: Access input_dev under mutex

## Summary
Severity: Medium
Advisory: CVE-2022-49538
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49538
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.13.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: jack: Access input_dev under mutex

It is possible when using ASoC that input_dev is unregistered while
calling snd_jack_report, which causes NULL pointer dereference.
In order to prevent this serialize access to input_dev using mutex lock.

## References
- https://git.kernel.org/stable/c/1b6a6fc5280e97559287b61eade2d4b363e836f2
- https://git.kernel.org/stable/c/582aea6084cc59fec881204f026816d1219f2348
- https://git.kernel.org/stable/c/5cc6f623f4818c7d7e9e966a45ebf324901ca9c5
- https://git.kernel.org/stable/c/74bab3bcf422593c582e47130aa8eb41ebb2dc09
- https://git.kernel.org/stable/c/8487a88136d54a1a4d3f26f1399685db648ab879
- https://git.kernel.org/stable/c/9e6a73b0c0f2014eb89249fb1640c5a3d58221c4
- https://git.kernel.org/stable/c/c093b62c40027c21d649c5534ad7aa3605a99b00
- https://git.kernel.org/stable/c/e2b8681769f6e205382f026b907d28aa5ec9d59a
- https://git.kernel.org/stable/c/f68bed124c7699e23ffb4ce4fcc84671e9193cde
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49538.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49538
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
