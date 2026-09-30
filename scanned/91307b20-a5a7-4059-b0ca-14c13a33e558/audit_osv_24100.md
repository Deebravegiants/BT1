# [H] wifi: iwlwifi: mvm: fix double list_add at iwl_mvm_mac_wake_tx_queue

## Summary
Severity: High
Advisory: CVE-2022-50164
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50164
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.4.211, >=5.5.0 <5.10.137, >=5.11.0 <5.15.61, >=5.16.0 <5.18.18, >=5.19.0 <5.19.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: iwlwifi: mvm: fix double list_add at iwl_mvm_mac_wake_tx_queue

After successfull station association, if station queues are disabled for
some reason, the related lists are not emptied. So if some new element is
added to the list in iwl_mvm_mac_wake_tx_queue, it can match with the old
one and produce a BUG like this:

[   46.535263] list_add corruption. prev->next should be next (ffff94c1c318a360), but was 0000000000000000. (prev=ffff94c1d02d3388).
[   46.535283] ------------[ cut here ]------------
[   46.535284] kernel BUG at lib/list_debug.c:26!
[   46.535290] invalid opcode: 0000 [#1] PREEMPT SMP PTI
[   46.585304] CPU: 0 PID: 623 Comm: wpa_supplicant Not tainted 5.19.0-rc3+ #1
[   46.592380] Hardware name: Dell Inc. Inspiron 660s/0478VN       , BIOS A07 08/24/2012
[   46.600336] RIP: 0010:__list_add_valid.cold+0x3d/0x3f
[   46.605475] Code: f2 4c 89 c1 48 89 fe 48 c7 c7 c8 40 67 93 e8 20 cc fd ff 0f 0b 48 89 d1 4c 89 c6 4c 89 ca 48 c7 c7 70 40 67 93 e8 09 cc fd ff <0f> 0b 48 89 fe 48 c7 c7 00 41 67 93 e8 f8 cb fd ff 0f 0b 48 89 d1
[   46.624469] RSP: 0018:ffffb20800ab76d8 EFLAGS: 00010286
[   46.629854] RAX: 0000000000000075 RBX: ffff94c1c318a0e0 RCX: 0000000000000000
[   46.637105] RDX: 0000000000000201 RSI: ffffffff9365e100 RDI: 00000000ffffffff
[   46.644356] RBP: ffff94c1c5f43370 R08: 0000000000000075 R09: 3064316334396666
[   46.651607] R10: 3364323064316334 R11: 39666666663d7665 R12: ffff94c1c5f43388
[   46.658857] R13: ffff94c1d02d3388 R14: ffff94c1c318a360 R15: ffff94c1cf2289c0
[   46.666108] FS:  00007f65634ff7c0(0000) GS:ffff94c1da200000(0000) knlGS:0000000000000000
[   46.674331] CS:  0010 DS: 0000 ES: 0000 CR0: 0000000080050033
[   46.680170] CR2: 00007f7dfe984460 CR3: 000000010e894003 CR4: 00000000000606f0
[   46.687422] Call Trace:
[   46.689906]  <TASK>
[   46.691950]  iwl_mvm_mac_wake_tx_queue+0xec/0x15c [iwlmvm]
[   46.697601]  ieee80211_queue_skb+0x4b3/0x720 [mac80211]
[   46.702973]  ? sta_info_get+0x46/0x60 [mac80211]
[   46.707703]  ieee80211_tx+0xad/0x110 [mac80211]
[   46.712355]  __ieee80211_tx_skb_tid_band+0x71/0x90 [mac80211]
...

In order to avoid this problem, we must also remove the related lists when
station queues are disabled.

## References
- https://git.kernel.org/stable/c/14a3aacf517a9de725dd3219dbbcf741e31763c4
- https://git.kernel.org/stable/c/182d3c1385f44ba7c508bf5b1292a7fe96ad4e9e
- https://git.kernel.org/stable/c/38d71acc15a2e72806b516380af0adb3830d4639
- https://git.kernel.org/stable/c/4a40af2b0b9517fca7ae2a030c9c0a16836303c0
- https://git.kernel.org/stable/c/5cca5f714fe6cedd2df9d8451ad8df21e6464f62
- https://git.kernel.org/stable/c/ff068c25bf90d26f0aee1751553f18076b797e8d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50164.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50164
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
