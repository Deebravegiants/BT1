# [?] common/wireaddr: Fix an out-of-bounds bug in the address parser

## Summary
Severity: Unknown
Chain: Bitcoin/Lightning
Component: ElementsProject/lightning
Published: 2025-06-06
Source: https://github.com/ElementsProject/lightning/commit/9fe88b430e65660fdd73a552827e92213f3c228f
Type: security-commit

## Details
common/wireaddr: Fix an out-of-bounds bug in the address parser

Changelog-Fixed: In `struct wireaddr`, the `addr` buffer is defined
with a length of DNS_ADDRLEN (255). When parsing a valid DNS name
that is exactly 255 bytes long, the subsequent attempt to append a
`NULL` terminator overruns the buffer and triggers an out-of-bounds
error under UBSan.

Fix this by removing the line that appends `NULL`. This change is
safe because the preceding call to:

`memset(&addr->addr, 0, sizeof(addr->addr))`

already zeroes the entire buffer.

## Patch
### common/wireaddr.c
```diff
@@ -48,7 +48,6 @@ bool fromwire_wireaddr(const u8 **cursor, size_t *max, struct wireaddr *addr)
 	case ADDR_TYPE_DNS:
 		addr->addrlen = fromwire_u8(cursor, max);
 		memset(&addr->addr, 0, sizeof(addr->addr));
-		addr->addr[addr->addrlen] = 0;
 		break;
 	default:
 		return false;
```
