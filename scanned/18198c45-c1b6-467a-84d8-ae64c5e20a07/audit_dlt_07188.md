# [?] lightningd: fix DF crash from libwally update.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2023-05-23
Source: https://github.com/ElementsProject/lightning/commit/ba46849ee26dbd4ef17a36838d75b3c6fd2e753c
Type: security-commit

## Details
lightningd: fix DF crash from libwally update.

Broken prior to 23.05 in 908f834d66218b52132c22af78a7ff87ad7ddec1:

```
lightningd: FATAL SIGNAL 11 (version d1cf88c)
0x56135ea0f865 send_backtrace
	common/daemon.c:33
0x56135ea0fa50 crashdump
	common/daemon.c:75
0x7f00d263bcef ???
	./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x56135e9887d9 validate_input_unspent
	lightningd/dual_open_control.c:2632
0x56135e989a55 handle_validate_inputs
	lightningd/dual_open_control.c:3026
0x56135e98a9a3 dual_opend_msg
	lightningd/dual_open_control.c:3357
0x56135e9df230 sd_msg_read
	lightningd/subd.c:557
0x56135eb0b6aa next_plan
	ccan/ccan/io/io.c:59
0x56135eb0c2d9 do_plan
	ccan/ccan/io/io.c:407
0x56135eb0c31b io_ready
	ccan/ccan/io/io.c:417
0x56135eb0e6b5 io_loop
	ccan/ccan/io/poll.c:453
0x56135e99b682 io_loop_with_timers
	lightningd/io_loop_with_timers.c:22
0x56135e9a230c main
	lightningd/lightningd.c:1231
0x7f00d262350f __libc_start_call_main
	../sysdeps/nptl/libc_start_call_main.h:58
0x7f00d26235c8 __libc_start_main_impl
	../csu/libc-start.c:381
0x56135e96ff24 ???
	???:0
0xffffffffffffffff ???
	???:0
```

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>
Changelog-EXPERIMENTAL: Fixed crash in dual-funding.

## Patch
### lightningd/dual_open_control.c
```diff
@@ -2602,7 +2602,7 @@ static void validate_input_unspent(struct bitcoind *bitcoind,
 		struct bitcoin_outpoint outpoint;
 
 		assert(pv->next_index > 0);
-		wally_tx_input_get_outpoint(&pv->psbt->tx->inputs[pv->next_index - 1],
+		wally_psbt_input_get_outpoint(&pv->psbt->inputs[pv->next_index - 1],
 					    &outpoint);
 
 		err = tal_fmt(pv, "Requested only confirmed"
@@ -2629,8 +2629,8 @@ static void validate_input_unspent(struct bitcoind *bitcoind,
 		if (serial % 2 != pv->role_to_validate)
 			continue;
 
-		wally_tx_input_get_outpoint(&pv->psbt->tx->inputs[i],
-					    &outpoint);
+		wally_psbt_input_get_outpoint(&pv->psbt->inputs[i],
+					      &outpoint);
 		pv->next_index = i + 1;
 
 		/* Confirm input is in a block */
```
