# [H]  Mistune: Potential DoS via quadratic-time parsing in parse_link_text

## Summary
Severity: High
Advisory: GHSA-qcq2-496w-v96p
CVE: CVE-2026-49851
CWE: CWE-1333, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-qcq2-496w-v96p
Type: github-advisory

## Affected
- PyPI: `mistune` — affected >=0 <3.3.0

## Details
### Summary
Mistune is vulnerable to a CPU exhaustion DoS due to superlinear (approximately O(n²)) behavior in parse_link_text. A relatively small input consisting of repeated [ characters causes significant parsing slowdown.

### Affected component
mistune/inline_parser.py → **parse_link_text**

### Description
When parsing Markdown containing many consecutive [ characters, parse_link_text repeatedly scans the input using a regex search inside a loop. Each iteration re-scans a large portion of the remaining string, resulting in quadratic-time behavior.
An attacker-controlled Markdown input can therefore trigger excessive CPU usage with a very small payload.

### Root cause
The vulnerability stems from a two-loop interaction:
- The outer loop in `InlineParser.parse()` (inline_parser.py) advances 
  only 1 character at a time when parse_link() returns None
- Each failed attempt calls `parse_link_text()` which performs an O(n) 
  scan to the end of the string looking for a closing `]`
- With n consecutive `[` characters, this results in O(n) × O(n) = O(n²) 
  total work

### PoC
Run below python script
```
import mistune
import time

md = mistune.create_markdown()

s = "[" * 6400

t = time.perf_counter()
md(s)
print(time.perf_counter() - t)
```
<img width="2028" height="1277" alt="image" src="https://github.com/user-attachments/assets/15d5bc0b-35f8-4a15-85e0-cbc314a45b06" />

**Benmark poc**
Run below code for benchmark
```
import mistune
import time

md = mistune.create_markdown()

sizes = [100,200,400,800,1600,3200,6400]

for n in sizes:
    s = "[" * n

    t0 = time.perf_counter()
    md(s)
    dt = time.perf_counter() - t0

    print(f"{n:6d} {dt:.6f}")
```
<img width="2503" height="1341" alt="image" src="https://github.com/user-attachments/assets/f09a7bbb-6927-4ba2-afb1-444dd913b84e" />


### Observed behaviour
```
python3 benchmark.py 
   100 0.001609
   200 0.003207
   400 0.012906
   800 0.050220
  1600 0.197307
  3200 0.801172
  6400 3.190393
```
Execution time grows superlinearly, consistent with O(n²) complex

### Impact
This can be used as a denial-of-service attack in any application that parses user-supplied Markdown using Mistune, including:

- Web applications (comments, posts, content rendering)
- API services processing Markdown
- Documentation rendering systems
- A small (~6 KB) payload can block CPU for multiple seconds.

### Suggested fix
Return the furthest scanned position from parse_link_text even on failure, so the outer loop can skip ahead instead of advancing 1 character at a time

### Security Classification
CWE-400: Uncontrolled Resource Consumption
Denial of Service (CPU exhaustion)

## References
- https://github.com/lepture/mistune/security/advisories/GHSA-qcq2-496w-v96p
- https://nvd.nist.gov/vuln/detail/CVE-2026-49851
- https://access.redhat.com/security/cve/CVE-2026-49851
- https://bugzilla.redhat.com/show_bug.cgi?id=2492304
- https://github.com/lepture/mistune
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-49851.json
