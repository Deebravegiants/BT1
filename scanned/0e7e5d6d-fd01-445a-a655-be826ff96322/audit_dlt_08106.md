# [?] plugin/pay: fix crash if failcodename isn't set.

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2024-08-12
Source: https://github.com/ElementsProject/lightning/commit/a243f3c79c9224a0d631503da2e94c35335f6c86
Type: security-commit

## Details
plugin/pay: fix crash if failcodename isn't set.

Fixes: https://github.com/ElementsProject/lightning/issues/7200
Signed-off-by: Rusty Russell <rusty@rustcorp.com.au>

## Patch
### plugins/libplugin-pay.c
```diff
@@ -2346,8 +2346,9 @@ static void payment_finished(struct payment *p)
 			json_add_u64(ret, "id", failure->id);
 
 			json_add_u32(ret, "failcode", failure->failcode);
-			json_add_string(ret, "failcodename",
-					failure->failcodename);
+			if (failure->failcodename)
+				json_add_string(ret, "failcodename",
+						failure->failcodename);
 
 			if (p->invstring)
 				json_add_invstring(ret, p->invstring);
```
