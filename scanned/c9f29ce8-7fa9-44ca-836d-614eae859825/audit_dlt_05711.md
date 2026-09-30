# [?] lightningd: fix crash in channel_control.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-10-22
Source: https://github.com/ElementsProject/lightning/commit/5a530e6c46974f86b4864903e668958ae8f412f5
Type: security-commit

## Details
lightningd: fix crash in channel_control.

I got a NULL deref on `infcopy->remote_funding = *inflight->funding->splice_remote_funding`
at once point in testing, so this should prevent that from happening,
yet still allow us to catch it in CI if it happens again.

Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### lightningd/channel_control.c
```diff
@@ -3,6 +3,7 @@
 #include <ccan/cast/cast.h>
 #include <ccan/tal/str/str.h>
 #include <channeld/channeld_wiregen.h>
+#include <common/daemon.h>
 #include <common/json_command.h>
 #include <common/psbt_open.h>
 #include <common/shutdown_scriptpubkey.h>
@@ -1818,6 +1819,11 @@ bool peer_start_channeld(struct channel *channel,
 		if (inflight->splice_locked_memonly)
 			continue;
 
+		if (!inflight->funding->splice_remote_funding) {
+			send_backtrace("Inflight has no splice_remote_funding?!");
+			continue;
+		}
+
 		infcopy = tal(inflights, struct inflight);
 
 		infcopy->remote_funding = *inflight->funding->splice_remote_funding;
```
