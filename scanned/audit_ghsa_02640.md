# [M] Memory Safety Issue when using patch or merge on state and assign the result back to state

## Summary
Severity: Medium
Advisory: GHSA-mc22-5q92-8v85
CVE: CVE-2021-39228
CWE: CWE-416, CWE-825
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-mc22-5q92-8v85
Type: github-advisory

## Affected
- crates.io: `tremor-script` — affected >=0.7.3 <0.11.6

## Details
### Impact

This vulnerability is a memory safety Issue when using [`patch`](https://www.tremor.rs/docs/tremor-script/index#patch) or [`merge`](https://www.tremor.rs/docs/tremor-script/index#merge) on `state` and assign the result back to `state`.
In this case affected versions of Tremor and the [tremor-script crate](https://crates.io/crates/tremor-script) maintains references to memory that might have been freed already. And these memory regions can be accessed by retrieving the `state`, e.g. send it over TCP or HTTP. This requires the Tremor server (or any other program using tremor-script) to execute a tremor-script script that uses the mentioned language construct.

#### Details

If affects the following two tremor-script language constructs:

* A [Merge](https://www.tremor.rs/docs/tremor-script/index#merge) where we assign the result back to the target expression
  and the expression to be merged needs to reference the `event`:

```
let state = merge state of event end;
```

* A [Patch](https://www.tremor.rs/docs/tremor-script/index#patch) where we assign the result back to the target expression
  and the patch operations used need to reference the `event`:

```
let state = patch state of insert event.key => event.value end;
```

For constructs like this (it does not matter what it references in the expression to be merged or the patch operations) an optimization
was applied to manipulate the target value in-place, instead of cloning it.

Our `Value` struct, which underpins all event data in `tremor-script`, is representing strings as borrowed `beef::Cow<'lifetime, str>`, 
that reference the raw data `Vec<u8>` the event is based upon. We keep this raw byte-array next to the `Value` structure inside our `Event` as a self-referential struct,
so we make sure that the structured `Value` and its references are valid across its whole lifetime.

The optimization was considered safe as long as it was only possible to merge or patch `event` data or static data.
When `state` was introduced to `tremor-script` (in version 0.7.3) a new possibility to keep `Value` data around for longer than the lifetime of an event emerged.
If `event` data is merged or patched into `state` without cloning it first, it can still reference keys or values from
the previous event, which will now be invalid. This allows access to those already freed regions of memory and to get their content out over the wire.

### Patches

The issue has been patched in https://crates.io/crates/tremor-script/0.11.6 and https://github.com/tremor-rs/tremor-runtime/releases/tag/v0.11.6 via commit [1a2efcd](https://github.com/tremor-rs/tremor-runtime/commit/1a2efcdbe68e5e7fd0a05836ac32d2cde78a0b2e) by removing the optimization
and always clone the target expression of a [Merge](https://www.tremor.rs/docs/tremor-script/index#merge) or [Patch](https://www.tremor.rs/docs/tremor-script/index#patch.

### Workarounds

If an upgrade is not possible, a possible workaround is to avoid the optimization
by introducing a temporary variable and not immediately reassigning to `state`:

```
let tmp = merge state of event end;
let state = tmp
```

### References

The actual fix is applied in this PR: https://github.com/tremor-rs/tremor-runtime/pull/1217

### For more information

If you have any questions or comments about this advisory:
* Open an issue on our repository [tremor-rs/tremor-runtime](https://github.com/tremor-rs/tremor-runtime)
* Please join our discord https://chat.tremor.rs and reach out to the team.

## References
- https://github.com/tremor-rs/tremor-runtime/security/advisories/GHSA-mc22-5q92-8v85
- https://nvd.nist.gov/vuln/detail/CVE-2021-39228
- https://github.com/tremor-rs/tremor-runtime/pull/1217
- https://github.com/tremor-rs/tremor-runtime/commit/1a2efcdbe68e5e7fd0a05836ac32d2cde78a0b2e
- https://github.com/tremor-rs/tremor-runtime
- https://github.com/tremor-rs/tremor-runtime/releases/tag/v0.11.6
