# [?] sql: fix crash for large channelmoves tables.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2026-04-08
Source: https://github.com/ElementsProject/lightning/commit/2ba55cc64b358659e5de682f7625817eb54a9f65
Type: security-commit

## Details
sql: fix crash for large channelmoves tables.

I've reworked this: in general we should clear the refresh bit before
calling the jsonrpc to do the update.  This allows the wait callback to
set the bit again if there's more to do, so we won't lose entries.

Now it's clear that we can remove the overzealous assert.

sql: plugins/sql.c:1749: refresh_by_created_index: Assertion `td->refresh_needs != REFRESH_UNNECESSARY' failed.
sql: FATAL SIGNAL 6 (version v26.04rc2)
0x5618e147892e send_backtrace
	common/daemon.c:38
0x5618e14789bb crashdump
	common/daemon.c:83
0x7f54d10ea04f ???
	./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
0x7f54d1138eec __pthread_kill_implementation
	./nptl/pthread_kill.c:44
0x7f54d10e9fb1 __GI_raise
	../sysdeps/posix/raise.c:26
0x7f54d10d4471 __GI_abort
	./stdlib/abort.c:79
0x7f54d10d4394 __assert_fail_base
	./assert/assert.c:94
0x7f54d10e2ec1 __GI___assert_fail
	./assert/assert.c:103
0x5618e1472725 refresh_by_created_index
	plugins/sql.c:1749
0x5618e14736af one_refresh_done
	plugins/sql.c:579
0x5618e1473932 limited_list_done
	plugins/sql.c:1738
0x5618e1477418 handle_rpc_reply
	plugins/libplugin.c:1093
0x5618e1477548 rpc_conn_read_response
	plugins/libplugin.c:1398
0x5618e147ec71 next_plan
	ccan/ccan/io/io.c:60

_Trimmed to 38 lines — full report: https://github.com/ElementsProject/lightning/commit/2ba55cc64b358659e5de682f7625817eb54a9f65_
