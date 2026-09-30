# [?] fix: Buffer overflow in home-screen plugin tagline formatting

## Summary
Severity: Unknown
Chain: Ledger
Component: LedgerHQ/app-ethereum
Published: 2026-05-11
Source: https://github.com/LedgerHQ/app-ethereum/commit/d235754574bc8e93eb9a7d3b8ea239cefc545e63
Type: security-commit

## Details
fix: Buffer overflow in home-screen plugin tagline formatting

The home-screen plugin tagline builder accumulated the FORMAT_PLUGIN
template length and the caller-controlled caller_app->name length into
a uint8_t. A sufficiently long caller name could wrap that accumulator,
leading to an undersized allocation for g_tag_line and a subsequent
snprintf overflow into adjacent memory across the on-device library-call
trust boundary.

Bound the plugin name with strnlen() against an explicit maximum and
perform the length math in size_t to make the wrap unreachable.

(cherry picked from commit 1191ba202dcef992614f68eb73c3d9080ec1ede5)

## Patch
### src/nbgl/ui_home.c
```diff
@@ -18,6 +18,20 @@ nbgl_warning_t warning;
 // Tagline format for plugins
 #define FORMAT_PLUGIN "This app enables clear\nsigning transactions for\nthe %s dApp."
 
+// Maximum caller-provided plugin name length we accept for the tagline. 64 is
+// generous compared to real Ledger plugin app names (typically < 20 chars) and
+// the fuzz harnesses' NAME_LENGTH=32, while staying well below the byte that
+// would let the total line length wrap. Any value below ~196 closes the
+// CWE-120 overflow.
+#define MAX_PLUGIN_NAME_LEN 64
+
+// Catch any future change to FORMAT_PLUGIN or MAX_PLUGIN_NAME_LEN that would
+// re-introduce a path where the tagline allocation length wraps. sizeof
+// includes the NUL terminator; 256 keeps a comfortable margin below the 8-bit
+// boundary that used to wrap the original uint8_t accumulator.
+_Static_assert(sizeof(FORMAT_PLUGIN) + MAX_PLUGIN_NAME_LEN < 256,
+               "Plugin tagline buffer math exceeds the historical 8-bit bound ");
+
 enum {
     TRANSACTION_CHECKS_TOKEN = FIRST_USER_TOKEN,
     BLIND_SIGNING_TOKEN,
@@ -243,14 +257,18 @@ static void prepare_and_display_home(const char *appname, const char *tagline, u
  */
 static void get_appname_and_tagline(const char **appname, const char **tagline) {
     uint64_t mainnet_chain_id;
-    uint8_t line_len = 1;  // Initialize lengths to 1 for '\0' character
 
     if (caller_app) {
         *appname = caller_app->name;
 
         if (caller_app->type == CALLER_TYPE_PLUGIN) {
-            line_len += strlen(FORMAT_PLUGIN);
-            line_len += strlen(caller_app->name);
+            size_t name_len = strnlen(caller_app->name, MAX_PLUGIN_NAME_LEN + 1);
+            if (name_len > MAX_PLUGIN_NAME_LEN) {
+                PRINTF("Plugin caller_app->name exceeds %u bytes; tagline omitted\n",
+                       (unsigned) MAX_PLUGIN_NAME_LEN);
+                return;
+            }
+            size_t line_len = 1 + strlen(FORMAT_PLUGIN) + name_len;
             // Allocate the buffer - will never be deallocated...
             if (APP_MEM_CALLOC((void **) &g_tag_line, line_len) == true) {
                 snprintf(g_tag_line, line_len, FORMAT_PLUGIN, *appname);
```
