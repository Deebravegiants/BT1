# [M] Unauthenticated denial-of-service via unbounded HPACK integer decoding in hpax

## Summary
Severity: Medium
Advisory: CVE-2026-58226
Aliases: EEF-CVE-2026-58226, GHSA-jj2p-32j7-whj2
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-58226
Type: osv

## Details
Inefficient Algorithmic Complexity vulnerability in elixir-mint hpax allows unauthenticated denial-of-service via unbounded HPACK integer decoding.

hpax decodes HPACK variable-length integers with no upper bound on the decoded value or the number of continuation octets. 'Elixir.HPAX.Types':decode_remaining_integer/3 accumulates the integer as int + (value <<< m), shifting by 7 more bits for each continuation octet and stopping only on a terminating octet or truncated input, never because the integer grew too large. Because BEAM integers are arbitrary precision, a run of N continuation octets builds an O(N)-bit bignum and re-adds into an ever-larger bignum on each step, so the total decoding cost is superlinear (about O(N^2)). An unauthenticated attacker who can send an HTTP/2 header block to a server using this decoder (reached through the 'Elixir.HPAX':decode/2 entry point) can supply a small header block that forces a large, attacker-controlled amount of CPU (and transient memory), a denial-of-service amplification.

This issue affects hpax from 0.1.1 before 1.0.4.

## References
- https://cna.erlef.org/cves/CVE-2026-58226.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-58226
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58226.json
- https://github.com/elixir-mint/hpax/security/advisories/GHSA-jj2p-32j7-whj2
- https://nvd.nist.gov/vuln/detail/CVE-2026-58226
- https://github.com/elixir-mint/hpax/commit/1ba4bb2dc91e80089cf89c73970ac3ded76f17eb
- https://github.com/elixir-mint/hpax
