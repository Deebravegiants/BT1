# [H] wifi: iwlegacy: Clear stale interrupts before resuming device

## Summary
Severity: High
Advisory: CVE-2024-50234
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-09
Source: https://osv.dev/vulnerability/CVE-2024-50234
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.25 <4.19.323, >=4.20.0 <5.4.285, >=5.5.0 <5.10.229, >=5.11.0 <5.15.171, >=5.16.0 <6.1.116, >=6.2.0 <6.6.60, >=6.7.0 <6.11.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlegacy: Clear stale interrupts before resuming device

iwl4965 fails upon resume from hibernation on my laptop. The reason
seems to be a stale interrupt which isn't being cleared out before
interrupts are enabled. We end up with a race beween the resume
trying to bring things back up, and the restart work (queued form
the interrupt handler) trying to bring things down. Eventually
the whole thing blows up.

Fix the problem by clearing out any stale interrupts before
interrupts get enabled during resume.

Here's a debug log of the indicent:
[   12.042589] ieee80211 phy0: il_isr ISR inta 0x00000080, enabled 0xaa00008b, fh 0x00000000
[   12.042625] ieee80211 phy0: il4965_irq_tasklet inta 0x00000080, enabled 0x00000000, fh 0x00000000
[   12.042651] iwl4965 0000:10:00.0: RF_KILL bit toggled to enable radio.
[   12.042653] iwl4965 0000:10:00.0: On demand firmware reload
[   12.042690] ieee80211 phy0: il4965_irq_tasklet End inta 0x00000000, enabled 0xaa00008b, fh 0x00000000, flags 0x00000282
[   12.052207] ieee80211 phy0: il4965_mac_start enter
[   12.052212] ieee80211 phy0: il_prep_station Add STA to driver ID 31: ff:ff:ff:ff:ff:ff
[   12.052244] ieee80211 phy0: il4965_set_hw_ready hardware  ready
[   12.052324] ieee80211 phy0: il_apm_init Init card's basic functions
[   12.052348] ieee80211 phy0: il_apm_init L1 Enabled; Disabling L0S
[   12.055727] ieee80211 phy0: il4965_load_bsm Begin load bsm
[   12.056140] ieee80211 phy0: il4965_verify_bsm Begin verify bsm
[   12.058642] ieee80211 phy0: il4965_verify_bsm BSM bootstrap uCode image OK
[   12.058721] ieee80211 phy0: il4965_load_bsm BSM write complete, poll 1 iterations
[   12.058734] ieee80211 phy0: __il4965_up iwl4965 is coming up
[   12.058737] ieee80211 phy0: il4965_mac_start Start UP work done.
[   12.058757] ieee80211 phy0: __il4965_down iwl4965 is going down
[   12.058761] ieee80211 phy0: il_scan_cancel_timeout Scan cancel timeout
[   12.058762] ieee80211 phy0: il_do_scan_abort Not performing scan to abort
[   12.058765] ieee80211 phy0: il_clear_ucode_stations Clearing ucode stations in driver
[   12.058767] ieee80211 phy0: il_clear_ucode_stations No active stations found to be cleared
[   12.058819] ieee80211 phy0: _il_apm_stop Stop card, put in low power state
[   12.058827] ieee80211 phy0: _il_apm_stop_master stop master
[   12.058864] ieee80211 phy0: il4965_clear_free_frames 0 frames on pre-allocated heap on clear.
[   12.058869] ieee80211 phy0: Hardware restart was requested
[   16.132299] iwl4965 0000:10:00.0: START_ALIVE timeout after 4000ms.
[   16.132303] ------------[ cut here ]------------
[   16.132304] Hardware became unavailable upon resume. This could be a software issue prior to suspend or a hardware issue.
[   16.132338] WARNING: CPU: 0 PID: 181 at net/mac80211/util.c:1826 ieee80211_reconfig+0x8f/0x14b0 [mac80211]
[   16.132390] Modules linked in: ctr ccm sch_fq_codel xt_tcpudp xt_multiport xt_state iptable_filter iptable_nat nf_nat nf_conntrack nf_defrag_ipv4 ip_tables x_tables binfmt_misc joydev mousedev btusb btrtl btintel btbcm bluetooth ecdh_generic ecc iTCO_wdt i2c_dev iwl4965 iwlegacy coretemp snd_hda_codec_analog pcspkr psmouse mac80211 snd_hda_codec_generic libarc4 sdhci_pci cqhci sha256_generic sdhci libsha256 firewire_ohci snd_hda_intel snd_intel_dspcfg mmc_core snd_hda_codec snd_hwdep firewire_core led_class iosf_mbi snd_hda_core uhci_hcd lpc_ich crc_itu_t cfg80211 ehci_pci ehci_hcd snd_pcm usbcore mfd_core rfkill snd_timer snd usb_common soundcore video parport_pc parport intel_agp wmi intel_gtt backlight e1000e agpgart evdev
[   16.132456] CPU: 0 UID: 0 PID: 181 Comm: kworker/u8:6 Not tainted 6.11.0-cl+ #143
[   16.132460] Hardware name: Hewlett-Packard HP Compaq 6910p/30BE, BIOS 68MCU Ver. F.19 07/06/2010
[   16.132463] Workqueue: async async_run_entry_fn
[   16.132469] RIP: 0010:ieee80211_reconfig+0x8f/0x14b0 [mac80211]
[   16.132501] Code: da 02 00 0
---truncated---

## References
- https://git.kernel.org/stable/c/07c90acb071b9954e1fecb1e4f4f13d12c544b34
- https://git.kernel.org/stable/c/23f9cef17ee315777dbe88d5c11ff6166e4d0699
- https://git.kernel.org/stable/c/271d282ecc15d7012e71ca82c89a6c0e13a063dd
- https://git.kernel.org/stable/c/8ac22fe1e2b104c37e4fecd97735f64bd6349ebc
- https://git.kernel.org/stable/c/8af8294d369a871cdbcdbb4d13b87d2d6e490a1f
- https://git.kernel.org/stable/c/9d89941e51259c2b0b8e9c10c6f1f74200d7444f
- https://git.kernel.org/stable/c/cedf0f1db8d5f3524339c2c6e35a8505b0f1ab73
- https://git.kernel.org/stable/c/d0231f43df473e2f80372d0ca150eb3619932ef9
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50234.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50234
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
