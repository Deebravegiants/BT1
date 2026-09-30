# [?] fix: ignore non-reentrant decorator when generating interface

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2021-01-25
Source: https://github.com/vyperlang/vyper/commit/c739c255eb9f5387a7d594c874647ffb89455468
Type: security-commit

## Details
fix: ignore non-reentrant decorator when generating interface

## Patch
### vyper/context/types/meta/interface.py
```diff
@@ -166,7 +166,7 @@ def _get_module_definitions(base_node: vy_ast.Module) -> Tuple[OrderedDict, Dict
     functions: OrderedDict = OrderedDict()
     events: Dict = {}
     for node in base_node.get_children(vy_ast.FunctionDef):
-        if "external" in [i.id for i in node.decorator_list]:
+        if "external" in [i.id for i in node.decorator_list if isinstance(i, vy_ast.Name)]:
             func = ContractFunction.from_FunctionDef(node)
             if node.name in functions:
                 # compare the input arguments of the new function and the previous one
```
