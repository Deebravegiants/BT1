# [H] ASoC: soc-core: flush delayed work before removing DAIs and widgets

## Summary
Severity: High
Advisory: CVE-2026-43459
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-05-08
Source: https://osv.dev/vulnerability/CVE-2026-43459
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.19, >=6.19.0 <6.19.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: soc-core: flush delayed work before removing DAIs and widgets

When a sound card is unbound while a PCM stream is open, a
use-after-free can occur in snd_soc_dapm_stream_event(), called from
the close_delayed_work workqueue handler.

During unbind, snd_soc_unbind_card() flushes delayed work and then
calls soc_cleanup_card_resources(). Inside cleanup,
snd_card_disconnect_sync() releases all PCM file descriptors, and
the resulting PCM close path can call snd_soc_dapm_stream_stop()
which schedules new delayed work with a pmdown_time timer delay.
Since this happens after the flush in snd_soc_unbind_card(), the
new work is not caught. soc_remove_link_components() then frees
DAPM widgets before this work fires, leading to the use-after-free.

The existing flush in soc_free_pcm_runtime() also cannot help as it
runs after soc_remove_link_components() has already freed the widgets.

Add a flush in soc_cleanup_card_resources() after
snd_card_disconnect_sync() (after which no new PCM closes can
schedule further delayed work) and before soc_remove_link_dais()
and soc_remove_link_components() (which tear down the structures the
delayed work accesses).

## References
- https://git.kernel.org/stable/c/231568afbc0cd25b8fb2a94ebf9738eabe1cf007
- https://git.kernel.org/stable/c/317a9298c54bb00319da73e5a7179f00e67fcbdf
- https://git.kernel.org/stable/c/3887e514978d28216246360b46a9cb534969eb5a
- https://git.kernel.org/stable/c/7d33e6140945482a07f8089ee86e13e02553ffdb
- https://git.kernel.org/stable/c/95bc5c225513fc3c4ce169563fb5e3929fbb938b
- https://git.kernel.org/stable/c/bf80a89da97285d9b877e0c6995e870d46b8025c
- https://git.kernel.org/stable/c/c054f0607c8bb1b1aa529bc109e4149298a1cccd
- https://git.kernel.org/stable/c/eab71e11ce2447c1e01809cbc11eab4234cf8dc8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43459.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43459
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
