# [H] BIT-lua-2020-24369

## Summary
Severity: High
Advisory: BIT-lua-2020-24369
Aliases: CVE-2020-24369
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-lua-2020-24369
Type: osv

## Affected
- Bitnami: `lua` — affected >=5.4.0 <5.4.1

## Details
ldebug.c in Lua 5.4.0 attempts to access debug information via the line hook of a stripped function, leading to a NULL pointer dereference.

## References
- https://github.com/lua/lua/commit/ae5b5ba529753c7a653901ffc29b5ea24c3fdf3a
- https://www.lua.org/bugs.html#5.4.0-12
- https://nvd.nist.gov/vuln/detail/CVE-2020-24369
