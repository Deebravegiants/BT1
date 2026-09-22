# [H] wifi: mac80211: fix use-after-free in chanctx code

## Summary
Severity: High
Advisory: CVE-2022-49416
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49416
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.17.0 <4.9.318, >=4.10.0 <4.14.283, >=4.15.0 <4.19.247, >=4.20.0 <5.4.198, >=5.5.0 <5.10.121, >=5.11.0 <5.15.46, >=5.16.0 <5.17.14, >=5.18.0 <5.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mac80211: fix use-after-free in chanctx code

In ieee80211_vif_use_reserved_context(), when we have an
old context and the new context's replace_state is set to
IEEE80211_CHANCTX_REPLACE_NONE, we free the old context
in ieee80211_vif_use_reserved_reassign(). Therefore, we
cannot check the old_ctx anymore, so we should set it to
NULL after this point.

However, since the new_ctx replace state is clearly not
IEEE80211_CHANCTX_REPLACES_OTHER, we're not going to do
anything else in this function and can just return to
avoid accessing the freed old_ctx.

## References
- https://git.kernel.org/stable/c/265bec4779a38b65e86a25120370f200822dfa76
- https://git.kernel.org/stable/c/2965c4cdf7ad9ce0796fac5e57debb9519ea721e
- https://git.kernel.org/stable/c/4ba81e794f0fad6234f644c2da1ae14d5b95e1c4
- https://git.kernel.org/stable/c/4f05a9e15edcdf5b97e0d86ab6ecd5f187289f6c
- https://git.kernel.org/stable/c/6118bbdf69f4718b02d26bbcf2e497eb66004331
- https://git.kernel.org/stable/c/82c8e7bbdd06c7ed58e22450cc5b37f33a25bb2c
- https://git.kernel.org/stable/c/88cc8f963febe192d6ded9df7217f92f380b449a
- https://git.kernel.org/stable/c/9f1e5cc85ad77e52f54049a94db0407445ae2a34
- https://git.kernel.org/stable/c/b79110f2bf6022e60e590d2e094728a8eec3e79e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49416.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49416
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
