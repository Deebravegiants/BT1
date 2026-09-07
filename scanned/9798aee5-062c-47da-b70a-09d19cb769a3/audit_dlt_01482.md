# [?] renepay: fix double free of tal object

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-06-11
Source: https://github.com/ElementsProject/lightning/commit/5e4eb7bdc3fc0d4a6cc9ddb455b8d898a98af912
Type: security-commit

## Details
renepay: fix double free of tal object

routefail object allocation was linked to route,
we had a crash of the plugin with the following error:

0x561f424fc07a send_backtrace
	common/daemon.c:33
0x561f424fc102 crashdump
	common/daemon.c:75
0x7f5b0e7dc04f ???
	???:0
0x7f5b0e82ae2c ???
	???:0
0x7f5b0e7dbfb1 ???
	???:0
0x7f5b0e7c6471 ???
	???:0
0x561f4252581f call_error
	ccan/ccan/tal/tal.c:95
0x561f425258c8 check_bounds
	ccan/ccan/tal/tal.c:169
0x561f425258f9 to_tal_hdr
	ccan/ccan/tal/tal.c:179
0x561f42526283 tal_free
	ccan/ccan/tal/tal.c:525
0x561f424e5379 routefail_end
	plugins/renepay/routefail.c:52
0x561f424e557b handle_failure
	plugins/renepay/routefail.c:431

apparently there was a race condition for which the route was first
freed before we arrived to routefail_end where we manually free
routefail. I don't see how this could have happened, but anyways
this subtle bug can be avoided by linking the routefail to the payment.

Signed-off-by: Lagrang3 <lagrang3@protonmail.com>
