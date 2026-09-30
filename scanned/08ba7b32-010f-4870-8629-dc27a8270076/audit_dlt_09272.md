# [?] fix: overflow checks and int128 LLL for `as_wei_value`

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2020-07-01
Source: https://github.com/vyperlang/vyper/commit/277b61790a0a77f9215a35b5cd4a6024abbea3e0
Type: security-commit

## Details
fix: overflow checks and int128 LLL for `as_wei_value`

## Patch
### vyper/functions/functions.py
```diff
@@ -52,7 +52,6 @@
     LLLnode,
     add_variable_offset,
     get_length,
-    get_number_as_fraction,
     getpos,
     make_byte_array_copier,
     make_byte_slice_copier,
@@ -945,38 +944,39 @@ def fetch_call_return(self, node):
     def build_LLL(self, expr, args, kwargs, context):
         value, denom_name = args[0], args[1].decode()
 
-        denom_divisor = next((v for k, v in self.wei_denoms.items() if denom_name in k), False)
-        if not denom_divisor:
-            raise InvalidLiteral(
-                f"Invalid denomination: {denom_name}, valid denominations are: "
-                f"{','.join(x[0] for x in self.wei_denoms)}",
-                expr.args[1],
-            )
-
-        # Compute the amount of wei and return that value
-        if isinstance(value, (int, Decimal)):
-            expr_args_0 = expr.args[0]
-            # On constant reference fetch value node of constant assignment.
-            if context.constants.ast_is_constant(expr.args[0]):
-                expr_args_0 = context.constants._constants_ast[expr.args[0].id]
-            numstring, num, den = get_number_as_fraction(expr_args_0, context)
-            if denom_divisor % den:
-                max_len = len(str(denom_divisor)) - 1
-                raise InvalidLiteral(
-                    f"Wei value of denomination '{denom_name}' has max {max_len} decimal places",
-                    expr.args[0],
-                )
-            sub = num * denom_divisor // den
-        elif value.typ.is_literal:
-            if value.value <= 0:
-                raise InvalidLiteral("Negative wei value not allowed", expr)
-            sub = ["mul", value.value, denom_divisor]
-        elif value.typ.typ == "uint256":
-            sub = ["mul", value, denom_divisor]
+        denom_divisor = next(v for k, v in self.wei_denoms.items() if denom_name in k)
+        if value.typ.typ == "uint256":
+            sub = [
+                "with",
+                "ans",
+                ["mul", value, denom_divisor],
+                [
+                    "seq",
+                    [
+                        "assert",
+                        ["or", ["eq", ["div", "ans", value], denom_divisor], ["iszero", value]],
+                    ],
+                    "ans",
+                ],
+            ]
+        elif value.typ.typ == "int128":
+            # signed types do not require bounds checks because the
+            # largest possible converted value will not overflow 2**256
+            sub = [
+                "seq",
+                ["assert", ["sgt", value, -1]],
+                ["mul", value, denom_divisor],
+            ]
+        elif value.typ.typ == "decimal":
+            sub = [
+                "seq",
+                ["assert", ["sgt", value, -1]],
+                ["div", ["mul", value, denom_divisor], DECIMAL_DIVISOR],
+            ]
         else:
-            sub = ["div", ["mul", value, denom_divisor], DECIMAL_DIVISOR]
+            raise CompilerPanic(f"Unexpected type: {value.typ.typ}")
 
-        return LLLnode.from_list(sub, typ=BaseType("uint256"), location=None, pos=getpos(expr),)
+        return LLLnode.from_list(sub, typ=BaseType("uint256"), location=None, pos=getpos(expr))
 
 
 zero_value = LLLnode.from_list(0, typ=BaseType("uint256"))
```
