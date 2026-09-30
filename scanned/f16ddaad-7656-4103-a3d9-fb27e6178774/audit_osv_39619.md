# [H] wifi: ath5k: do not access array OOB

## Summary
Severity: High
Advisory: CVE-2026-46307
Ecosystem: Linux
CVSS: 8.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:L)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-46307
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.0.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.140, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath5k: do not access array OOB

Vincent reports:
> The ath5k driver seems to do an array-index-out-of-bounds access as
> shown by the UBSAN kernel message:
> UBSAN: array-index-out-of-bounds in drivers/net/wireless/ath/ath5k/base.c:1741:20
> index 4 is out of range for type 'ieee80211_tx_rate [4]'
> ...
> Call Trace:
>  <TASK>
>  dump_stack_lvl+0x5d/0x80
>  ubsan_epilogue+0x5/0x2b
>  __ubsan_handle_out_of_bounds.cold+0x46/0x4b
>  ath5k_tasklet_tx+0x4e0/0x560 [ath5k]
>  tasklet_action_common+0xb5/0x1c0

It is real. 'ts->ts_final_idx' can be 3 on 5212, so:
   info->status.rates[ts->ts_final_idx + 1].idx = -1;
with the array defined as:
   struct ieee80211_tx_rate rates[IEEE80211_TX_MAX_RATES];
while the size is:
   #define IEEE80211_TX_MAX_RATES  4
is indeed bogus.

Set this 'idx = -1' sentinel only if the array index is less than the
array size. As mac80211 will not look at rates beyond the size
(IEEE80211_TX_MAX_RATES).

Note: The effect of the OOB write is negligible. It just overwrites the
next member of info->status, i.e. ack_signal.

## References
- https://git.kernel.org/stable/c/568173ad9bd0b46cc6cd937dea8791e9b5eefa57
- https://git.kernel.org/stable/c/744c19e266b0d2628c5951439195dcef27eadacf
- https://git.kernel.org/stable/c/83226c71af53fb9b3cad40cb9a9a79f36d68c020
- https://git.kernel.org/stable/c/9dd6aae4bc7bfa11088d928670a3315eae542769
- https://git.kernel.org/stable/c/d6869537013b1f21b292342752d97868b79b5934
- https://git.kernel.org/stable/c/d748603f12baff112caa3ab7d39f50100f010dbd
- https://git.kernel.org/stable/c/e9f1081bc775146156def0dbc821b92f35d56afb
- https://git.kernel.org/stable/c/ecb1c163166759dec004c1fdb9709b8a5992fc8e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46307.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46307
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
