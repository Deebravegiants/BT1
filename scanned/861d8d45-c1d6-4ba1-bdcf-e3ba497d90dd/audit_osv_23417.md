# [H] ALSA: hda: Fix UAF of leds class devs at unbinding

## Summary
Severity: High
Advisory: CVE-2022-48735
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-06-20
Source: https://osv.dev/vulnerability/CVE-2022-48735
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.10.99, >=5.11.0 <5.15.22, >=5.16.0 <5.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: hda: Fix UAF of leds class devs at unbinding

The LED class devices that are created by HD-audio codec drivers are
registered via devm_led_classdev_register() and associated with the
HD-audio codec device.  Unfortunately, it turned out that the devres
release doesn't work for this case; namely, since the codec resource
release happens before the devm call chain, it triggers a NULL
dereference or a UAF for a stale set_brightness_delay callback.

For fixing the bug, this patch changes the LED class device register
and unregister in a manual manner without devres, keeping the
instances in hda_gen_spec.

## References
- https://git.kernel.org/stable/c/0e629052f013eeb61494d4df2f1f647c2a9aef47
- https://git.kernel.org/stable/c/549f8ffc7b2f7561bea7f90930b6c5104318e87b
- https://git.kernel.org/stable/c/813e9f3e06d22e29872d4fd51b54992d89cf66c8
- https://git.kernel.org/stable/c/a7de1002135cf94367748ffc695a29812d7633b5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48735.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48735
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
