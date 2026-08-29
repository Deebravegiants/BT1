# [?] lightningd: fix crash on fixup scan if block unavailable.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-12-04
Source: https://github.com/ElementsProject/lightning/commit/22f7a620e6bc6533128517eb987ef763ee24a738
Type: security-commit

## Details
lightningd: fix crash on fixup scan if block unavailable.

```
lightningd: FATAL SIGNAL 11 (version v25.12rc3-1-g498c5b6)
0x5cc2f620ce4c send_backtrace
        common/daemon.c:38
0x5cc2f620cee8 crashdump
        common/daemon.c:83
0x7e3ac1e4532f ???
        ./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x5cc2f615f186 fixup_scan_block
        lightningd/chaintopology.c:1531
0x5cc2f615c22c getrawblockbyheight_callback
        lightningd/bitcoind.c:484
0x5cc2f61aee87 plugin_response_handle
        lightningd/plugin.c:701
0x5cc2f61b4043 plugin_read_json
        lightningd/plugin.c:790
0x5cc2f6248d8b next_plan
        ccan/ccan/io/io.c:60
0x5cc2f624925c do_plan
        ccan/ccan/io/io.c:422
0x5cc2f6249319 io_ready
        ccan/ccan/io/io.c:439
0x5cc2f624ad24 io_loop
        ccan/ccan/io/poll.c:470
0x5cc2f618381a io_loop_with_timers
        lightningd/io_loop_with_timers.c:22
0x5cc2f61892ff main
```

This happens intermittantly on in a few tests:

tests/test_invoices.py::test_invoice_botched_migration
tests/test_pay.py::test_pay_bolt11_metadata
tests/test_runes.py::test_id_migration

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

_Trimmed to 38 lines — full report: https://github.com/ElementsProject/lightning/commit/22f7a620e6bc6533128517eb987ef763ee24a738_
