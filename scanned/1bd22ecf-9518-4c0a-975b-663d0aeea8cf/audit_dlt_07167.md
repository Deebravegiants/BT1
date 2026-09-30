# [?] trace: minimal fix to avoid crash when > 128 traces active.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-03-31
Source: https://github.com/ElementsProject/lightning/commit/ee2ec8befa88dbfc2bbcf80f871420bcdc369207
Type: security-commit

## Details
trace: minimal fix to avoid crash when > 128 traces active.

chanbackup with many peers can do more than 128 concurrent rpc commands.
autoclean is the other plugin which can do many requests at once, so I
expect a similar issue there.

I tested this by rebuilding with `MAX_ACTIVE_SPANS` 1, which autoclean
tests triggered immediately.

The real fix is probably to use a hash table with a large initial size.

```
Mar 24 06:30:45 mlbb2 sh[28000]: chanbackup: common/trace.c:190: trace_span_slot: Assertion `s' failed.
Mar 24 06:30:45 mlbb2 sh[28000]: chanbackup: FATAL SIGNAL 6 (version v25.02)
Mar 24 06:30:45 mlbb2 sh[28000]: 0x5575232bac4f send_backtrace
Mar 24 06:30:45 mlbb2 sh[28000]:         common/daemon.c:33
Mar 24 06:30:45 mlbb2 sh[28000]: 0x5575232baceb crashdump
Mar 24 06:30:45 mlbb2 sh[28000]:         common/daemon.c:78
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958cd851f ???
Mar 24 06:30:45 mlbb2 sh[28000]:         ./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958d2c9fc __pthread_kill_implementation
Mar 24 06:30:45 mlbb2 sh[28000]:         ./nptl/pthread_kill.c:44
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958d2c9fc __pthread_kill_internal
Mar 24 06:30:45 mlbb2 sh[28000]:         ./nptl/pthread_kill.c:78
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958d2c9fc __GI___pthread_kill
Mar 24 06:30:45 mlbb2 sh[28000]:         ./nptl/pthread_kill.c:89
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958cd8475 __GI_raise
Mar 24 06:30:45 mlbb2 sh[28000]:         ../sysdeps/posix/raise.c:26
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958cbe7f2 __GI_abort
Mar 24 06:30:45 mlbb2 sh[28000]:         ./stdlib/abort.c:79
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958cbe71a __assert_fail_base
Mar 24 06:30:45 mlbb2 sh[28000]:         ./assert/assert.c:94
Mar 24 06:30:45 mlbb2 sh[28000]: 0x7f2958ccfe95 __GI___assert_fail
Mar 24 06:30:45 mlbb2 sh[28000]:         ./assert/assert.c:103
Mar 24 06:30:45 mlbb2 sh[28000]: 0x5575232ab7fa trace_span_slot
Mar 24 06:30:45 mlbb2 sh[28000]:         common/trace.c:190
Mar 24 06:30:45 mlbb2 sh[28000]: 0x5575232abc9f trace_span_start
Mar 24 06:30:45 mlbb2 sh[28000]:         common/trace.c:267
Mar 24 06:30:45 mlbb2 sh[28000]: 0x5575232a7c34 send_outreq
Mar 24 06:30:45 mlbb2 sh[28000]:         plugins/libplugin.c:1112
```

Changelog-Fixed: autoclean/chanbackup: fixed tracepoint crash on large number of requests.
Fixes: https://github.com/ElementsProject/lightning/issues/8177
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### common/trace.c
```diff
@@ -10,9 +10,10 @@
 #include <common/trace.h>
 #include <sodium/randombytes.h>
 #include <stdio.h>
+#include <unistd.h>
 
 #if HAVE_USDT
-#include <sys/sdt.h>
+  #include <sys/sdt.h>
 
 #define MAX_ACTIVE_SPANS 128
 
@@ -40,6 +41,7 @@
 #endif
 
 const char *trace_service_name = "lightningd";
+static bool disable_trace = false;
 
 struct span_tag {
 	char *name, *value;
@@ -176,6 +178,9 @@ static struct span *trace_span_find(size_t key)
 	return NULL;
 }
 
+/* FIXME: Forward declaration for minimal patch size */
+static void trace_span_clear(struct span *s);
+
 /**
  * Find an empty slot for a new span.
  */
@@ -187,7 +192,13 @@ static struct span *trace_span_slot(void)
 
 	/* Might end up here if we have more than MAX_ACTIVE_SPANS
 	 * concurrent spans. */
-	assert(s);
+	if (!s) {
+		fprintf(stderr, "%u: out of spans, disabling tracing\n", getpid());
+		for (size_t i = 0; i < MAX_ACTIVE_SPANS; i++)
+			trace_span_clear(&active_spans[i]);
+		disable_trace = true;
+		return NULL;
+	}
 	assert(s->parent == NULL);
 
 	/* Be extra careful not to create cycles. If we return the
@@ -260,11 +271,15 @@ void trace_span_start(const char *name, const void *key)
 	size_t numkey = trace_key(key);
 	struct timeabs now = time_now();
 
+	if (disable_trace)
+		return;
 	trace_init();
 	trace_check_tree();
 
 	assert(trace_span_find(numkey) == NULL);
 	struct span *s = trace_span_slot();
+	if (!s)
+		return;
 	s->key = numkey;
 	randombytes_buf(s->id, SPAN_ID_SIZE);
 	s->start_time = (now.ts.tv_sec * 1000000) + now.ts.tv_nsec / 1000;
@@ -293,6 +308,9 @@ void trace_span_remote(u8 trace_id[TRACE_ID_SIZE], u8 span_id[SPAN_ID_SIZE])
 
 void trace_span_end(const void *key)
 {
+	if (disable_trace)
+		return;
+
 	size_t numkey = trace_key(key);
 	struct span *s = trace_span_find(numkey);
 	assert(s && "Span to end not found");
@@ -323,6 +341,9 @@ void trace_span_end(const void *key)
 
 void trace_span_tag(const void *key, const char *name, const char *value)
 {
+	if (disable_trace)
+		return;
+
 	size_t numkey = trace_key(key);
 	struct span *span = trace_span_find(numkey);
 	assert(span);
@@ -341,6 +362,9 @@ void trace_span_tag(const void *key, const char *name, const char *value)
 
 void trace_span_suspend_(const void *key, const char *lbl)
 {
+	if (disable_trace)
+		return;
+
 	size_t numkey = trace_key(key);
 	struct span *span = trace_span_find(numkey);
 	TRACE_DBG("Suspending span %s (%zu)\n", current->name, current->key);
@@ -351,6 +375,9 @@ void trace_span_suspend_(const void *key, const char *lbl)
 
 void trace_span_resume_(const void *key, const char *lbl)
 {
+	if (disable_trace)
+		return;
+
 	size_t numkey = trace_key(key);
 	current = trace_span_find(numkey);
 	TRACE_DBG("Resuming span %s (%zu)\n", current->name, current->key);
```
