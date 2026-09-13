# [M] ASoC: mediatek: Fix error handling in mt8173_max98090_dev_probe

## Summary
Severity: Medium
Advisory: CVE-2022-49514
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49514
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: mediatek: Fix error handling in mt8173_max98090_dev_probe

Call of_node_put(platform_node) to avoid refcount leak in
the error path.

## References
- https://git.kernel.org/stable/c/0a1901f34f775b83ea4b8dbb5ed992147b9b8531
- https://git.kernel.org/stable/c/1e932aba3c7628c9f880ee9c2cfcc2ae3ba0c01e
- https://git.kernel.org/stable/c/23f340ed906c758cec6527376768e3bc1474ac30
- https://git.kernel.org/stable/c/48889eb3cce91d7f58e02bc07277b7f724b7a54a
- https://git.kernel.org/stable/c/4f4e0454e226de3bf4efd7e7924d1edc571c52d5
- https://git.kernel.org/stable/c/98d5afe868df998b0244f4c229ab758b4083684a
- https://git.kernel.org/stable/c/cc43b9fdca519c5b13be6a717bacbebccd628cf6
- https://git.kernel.org/stable/c/ebd5cb4f1f3f10b839e7575219e0f17b60c23113
- https://git.kernel.org/stable/c/fb66e0512e5ccc093070e21cf88cce8d98c181b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49514.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49514
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
