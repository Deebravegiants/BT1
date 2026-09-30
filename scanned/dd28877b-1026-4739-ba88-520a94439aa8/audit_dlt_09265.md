# [?] docs: add security advisory note for `ecrecover` (#3539)

## Summary
Severity: Unknown
Chain: Vyper
Component: vyperlang/vyper
Published: 2023-08-07
Source: https://github.com/vyperlang/vyper/commit/728a27677240fdd55a4144d04b31004f8330847c
Type: security-commit

## Details
docs: add security advisory note for `ecrecover` (#3539)

Co-authored-by: Charles Cooper <cooper.charles.m@gmail.com>

## Patch
### docs/built-in-functions.rst
```diff
@@ -379,7 +379,11 @@ Cryptography
     * ``s``: second 32 bytes of signature
     * ``v``: final 1 byte of signature
 
-    Returns the associated address, or ``0`` on error.
+    Returns the associated address, or ``empty(address)`` on error.
+
+    .. note::
+
+         Prior to Vyper ``0.3.10``, the ``ecrecover`` function could return an undefined (possibly nonzero) value for invalid inputs to ``ecrecover``. For more information, please see `GHSA-f5x6-7qgp-jhf3 <https://github.com/vyperlang/vyper/security/advisories/GHSA-f5x6-7qgp-jhf3>`_.
 
     .. code-block:: python
 
```
