# [H] UltraJSON has an integer overflow handling large indent leads to buffer overflow or infinite loop

## Summary
Severity: High
Advisory: GHSA-c8rr-9gxc-jprv
CVE: CVE-2026-32875
CWE: CWE-190, CWE-787, CWE-835
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-c8rr-9gxc-jprv
Type: github-advisory

## Affected
- PyPI: `ujson` — affected >=5.1.0 <5.12.0

## Details
### Summary

`ujson.dumps()` crashes the Python interpreter (segmentation fault) when the product of the `indent` parameter and the nested depth of the input exceeds INT32_MAX. It can also get stuck in an infinite loop if the `indent` is a large negative number. Both are caused by an integer overflow/underflow whilst calculating how much memory to reserve for indentation. And both can be used to achieve denial of service.

(Note: A negative indent to `ujson` means add spaces after colons but do not add line breaks or indentation. It is unclear to the current maintainers whether this was ever even an intended feature or just a byproduct of the way it was written.)

### Exploitability

To be vulnerable, a service must call `ujson.dump()`/`ujson.dumps()`/`ujson.encode()` whilst giving untrusted users control over the `indent` parameter and not restrict that indentation to reasonably small non-negative values. (Even with the fix for this vulnerability, such usage is strongly advised against since even a bug-free JSON serialiser would be vulnerable to denial of service simply by the attacker requesting indents that have the server needlessly filling out gigabytes of whitespace.)

A service may also be vulnerable to the infinite loop if it uses a fixed _negative_ `indent`. An underflow always occurs for any negative indent when the input data is at least one level nested but, for small negative indents, the underflow is usually accidentally rectified by another overflow. As far as the maintainers are aware, the infinite loop can not be reached for indentations from -1 to -65536 / max_recursion_depth_as_limited_by_stack_size but users of negative indents are encouraged to consider their service affected even if the infinite loop seems unreachable.

### Example

```python
import ujson

def example(depth, indent):
    a = [0]
    for i in range(1000):
        a = [a]
    ujson.dumps(a, indent=indent)

example(1, 2**30)  # segfault
example(1000, -200)  # infinite loop
```

### Patches

ujson 5.12.0, containing 486bd4553dc471a1de11613bc7347a6b318e37ea, promotes the integer types where the overflow occurred, skips the indentation code path for negative indent (which was supposed to be a no-op) and places an artificial cap of 1000 on the `indent` parameter.

### Workarounds

Users who don't wish to upgrade can either use a fixed indentation, no indentation or ensure indentation is non-negative and not enormous (below `2**31 / max_recursion_depth_as_limited_by_stack_size`).

### References

The original bug report can be found at https://github.com/ultrajson/ultrajson/issues/700

This issue was independently discovered by @coco1629, @EthanKim88 and @vmfunc.

## References
- https://github.com/ultrajson/ultrajson/security/advisories/GHSA-c8rr-9gxc-jprv
- https://nvd.nist.gov/vuln/detail/CVE-2026-32875
- https://github.com/ultrajson/ultrajson/issues/700
- https://github.com/ultrajson/ultrajson/commit/486bd4553dc471a1de11613bc7347a6b318e37ea
- https://github.com/ultrajson/ultrajson
