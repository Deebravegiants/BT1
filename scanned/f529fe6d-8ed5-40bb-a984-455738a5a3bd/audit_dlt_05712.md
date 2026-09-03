# [?] htlc_wire: fix crash when adding an HTLC

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-08-26
Source: https://github.com/ElementsProject/lightning/commit/7e5cf41b4e5cd11064f3a8bcb63ec2edb2ea1dae
Type: security-commit

## Details
htlc_wire: fix crash when adding an HTLC

In line channeld/channeld_wiregen.c:832 `*added+i` is not a tal object hence
the instruction in common/htlc_wire.c:200 `tal_arr(ctx, struct tlv_field, 0);` crashes CLN.
This is fixed by stating that added_htlc is a a varsize_type.

Logs:

2025-08-16T02:25:28.640Z **BROKEN** lightningd: FATAL SIGNAL 6 (version v25.05-200-g79b959b)V
...
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:95 (call_error) 0x54f6bc
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:169 (check_bounds) 0x54f75a
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:178 (to_tal_hdr) 0x54f782
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:193 (to_tal_hdr_or_null) 0x54f7c7
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:471 (tal_alloc_) 0x54ffe4
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/tal/tal.c:517 (tal_alloc_arr_) 0x5500c4
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: common/htlc_wire.c:200 (fromwire_len_and_tlvstream) 0x48d63d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: common/htlc_wire.c:234 (fromwire_added_htlc) 0x48dd23
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: channeld/channeld_wiregen.c:832 (fromwire_channeld_got_commitsig) 0x4c61fa
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/peer_htlcs.c:2377 (peer_got_commitsig) 0x4549cb
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/channel_control.c:1552 (channel_msg) 0x4140fe
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/subd.c:560 (sd_msg_read) 0x461513
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:60 (next_plan) 0x544885
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:422 (do_plan) 0x544cea
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/io.c:439 (io_ready) 0x544d9d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: ccan/ccan/io/poll.c:455 (io_loop) 0x54665d
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/io_loop_with_timers.c:22 (io_loop_with_timers) 0x42d220
2025-08-16T02:25:28.640Z **BROKEN** lightningd: backtrace: lightningd/lightningd.c:1487 (main) 0x43280f

gdb inspection:
830             *added = num_added ? tal_arr(ctx, struct added_htlc, num_added) : NULL;
831             for (size_t i = 0; i < num_added; i++)
832                     fromwire_added_htlc(&cursor, &plen, *added + i);
(gdb) p i
$3 = 1

Changelog-None: crash introduced this release.
Signed-off-by: Lagrang3 <lagrang3@protonmail.com>

_Trimmed to 38 lines — full report: https://github.com/ElementsProject/lightning/commit/7e5cf41b4e5cd11064f3a8bcb63ec2edb2ea1dae_
