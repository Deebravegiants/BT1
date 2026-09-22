# [M] Pow Mnesia cache doesn't invalidate all expired keys on startup

## Summary
Severity: Medium
Advisory: GHSA-3cjh-p6pw-jhv9
CVE: CVE-2023-42446
CWE: CWE-298, CWE-672
Ecosystem: Hex
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2023-09-19
Source: https://github.com/advisories/GHSA-3cjh-p6pw-jhv9
Type: github-advisory

## Affected
- Hex: `pow` — affected >=1.0.14 <1.0.34

## Details
Use of `Pow.Store.Backend.MnesiaCache` is susceptible to session hijacking as expired keys are not being invalidated correctly on startup. A cache key may become expired when all `Pow.Store.Backend.MnesiaCache` instances have been shut down for a period that is longer than the keys' remaining TTL and the expired key won't be invalidated on startups.

### Workarounds

The expired keys, including all expired sessions, can be manually invalidated by running:

```elixir
:mnesia.sync_transaction(fn ->
  Enum.each(:mnesia.dirty_select(Pow.Store.Backend.MnesiaCache, [{{Pow.Store.Backend.MnesiaCache, :_, :_}, [], [:"$_"]}]), fn {_, key,  {_value, expire}} ->
    ttl = expire - :os.system_time(:millisecond)
    if ttl < 0, do: :mnesia.delete({Pow.Store.Backend.MnesiaCache, key})
  end)
end)
```

### References
https://github.com/pow-auth/pow/commit/15dc525be03c466daa5d2119ca7acdec7b24ed17
https://github.com/pow-auth/pow/issues/713
https://github.com/pow-auth/pow/pull/714

## References
- https://github.com/pow-auth/pow/security/advisories/GHSA-3cjh-p6pw-jhv9
- https://nvd.nist.gov/vuln/detail/CVE-2023-42446
- https://github.com/pow-auth/pow/issues/713
- https://github.com/pow-auth/pow/pull/714
- https://github.com/pow-auth/pow/commit/15dc525be03c466daa5d2119ca7acdec7b24ed17
- https://github.com/pow-auth/pow
