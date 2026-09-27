# [M] Incorrect Output of Incremental Portable SHAKE API on Multiple Squeeze Calls

## Summary
Severity: Medium
Advisory: RUSTSEC-2026-0207
Ecosystem: crates.io
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/RUSTSEC-2026-0207
Type: osv

## Affected
- crates.io: `libcrux-sha3` — affected >=0.0.0-0 <0.0.10

## Details
The incremental squeeze functions in the portable SHAKE XOF API, when
attempting to squeeze an output using multiple calls to `squeeze`,
rather than squeezing the full output at once, could output incorrect
values. Internally, output blocks that were not completely squeezed
were not buffered for the next call to `squeeze`, which would
consequently drop bytes of the correct squeeze output if the preceding
call requested an output of length in bytes not cleanly divisible by
`RATE` (168 for SHAKE128, 136 for SHAKE256).

## Impact
This bug impacts users that rely on this XOF API to squeeze output in
multiple calls where any of the calls request an output length that is
not divisible by `RATE`. It does not impact the use of libcrux-sha3 in
libcrux-ml-kem or libcrux-ml-dsa.

## Mitigation
Starting from version `0.0.10` the squeeze functions correctly output
all squeezed bytes independent of the number of `squeeze` calls and
the output lengths requested in each call.

## References
- https://crates.io/crates/libcrux-sha3
- https://rustsec.org/advisories/RUSTSEC-2026-0207.html
- https://github.com/celabshq/libcrux/pull/1389
