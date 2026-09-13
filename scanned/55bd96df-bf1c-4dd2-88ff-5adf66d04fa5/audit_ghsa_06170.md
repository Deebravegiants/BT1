# [H] icalendar has Algorithmic Complexity in Equality

## Summary
Severity: High
Advisory: GHSA-cv84-9p8j-fj68
CVE: CVE-2026-55099
CWE: CWE-400, CWE-407
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-cv84-9p8j-fj68
Type: github-advisory

## Affected
- PyPI: `icalendar` — affected >=7.1.0 <7.1.3

## Details
### Summary

`Component.__eq__` compares subcomponents in `O(2^n)` time relative to nesting depth. Because the parser accepts arbitrarily nested components, a sub-kilobyte `.ics` file is enough to make a single equality check run for minutes or hang indefinitely. Any application that compares parsed components (`==`, `!=`, `in`, set/dict membership, deduplication, test assertions) against attacker-supplied calendar data is exposed to denial of service.

### Details

`Component` subclasses `dict` and stores children in a separate `subcomponents` list. `__eq__` (`src/icalendar/cal/component.py:642-665`) checks set-equivalence of children with two membership loops:

```python
def __eq__(self, other):
    if len(self.subcomponents) != len(other.subcomponents):
        return False
    if not super().__eq__(other):
        return False
    for subcomponent in self.subcomponents:
        if subcomponent not in other.subcomponents:
            return False
    for subcomponent in other.subcomponents:
        if subcomponent not in self.subcomponents:
            return False
    return True
```

Each `... not in ...` test invokes `__eq__` on the children. For a nested chain, both loops descend the full subtree, so each level spawns two recursive comparisons: `T(n) = 2·T(n-1)` → `O(2^n)`.

Parsing does not gate this. `Component.from_ical` builds the structure iteratively and imposes no depth limit, so `BEGIN:VEVENT` blocks can be nested to any depth (parsing the payload below is instant). The cost is paid only when a comparison occurs, and only when the operands are equal far enough down to keep both loops recursing, a condition the attacker controls by submitting equal subtrees.

### PoC

```python
from icalendar import Calendar

d = 26
event = b"BEGIN:VEVENT\r\n" * d + b"END:VEVENT\r\n" * d
ics = b"BEGIN:VCALENDAR\r\n" + event + event + b"END:VCALENDAR\r\n"

cal = Calendar.from_ical(ics)
a, b = cal.subcomponents
a == b
```

Measured on `icalendar` 7.1.x, CPython 3.14:

| Payload | Depth | `==` time |
|---|---|---|
| 552 B | 20 | 0.76 s |
| 656 B | 24 | 12 s |
| 708 B | 26 | 48 s |
| ~800 B | 30 | ~13 min |

A single uploaded file supplies both operands (two identical nested events), so no second input is needed. The same blowup occurs in round-trip checks (`cal == Calendar.from_ical(cal.to_ical())`) and in any membership/dedup logic over subcomponents.

### Impact

Algorithmic-complexity denial of service (CWE-407). Unauthenticated; a few hundred bytes of input pin a CPU core indefinitely. It affects any service that parses untrusted iCalendar data and then compares components for equality or membership, including calendar sync/import endpoints, invite processing, dedup, and round-trip/normalization checks. It is not triggered by parsing alone, and a comparison against an early-differing object short-circuits harmlessly, so impact is limited to code paths that perform such comparisons.

### Fix

`Component.__eq__` rewritten to walk an explicit stack instead of recursing, matching each pair of nested components exactly once. Equality is now linear in the number of components and preserves the existing multiset equivalence and commutativity semantics.

## References
- https://github.com/collective/icalendar/security/advisories/GHSA-cv84-9p8j-fj68
- https://github.com/collective/icalendar/commit/b6b2608ae3af6de40695b4e40f71847485aa0b49
- https://github.com/collective/icalendar/commit/cad40cd112c93fd142ec12cc5b37445a849b8a79
- https://github.com/collective/icalendar
- https://github.com/collective/icalendar/releases/tag/v7.1.3
