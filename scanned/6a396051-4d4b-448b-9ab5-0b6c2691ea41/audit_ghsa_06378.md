# [M] tornado: multipart split() creates huge temp list before max_parts check -> memory amplification DoS (httputil.py:34)

## Summary
Severity: Medium
Advisory: GHSA-8423-8fgw-73vq
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-8423-8fgw-73vq
Type: github-advisory

## Affected
- PyPI: `tornado` — affected >=0 <6.5.8

## Details
## Description

### Summary

`parse_multipart_form_data` (httputil.py:34) calls
`data.split(b"--"+boundary+b"\r\n")` **before** the `max_parts` check (:35).
A 600KB body with 100k parts creates a 100k-element transient list first,
then rejects   transient memory amplification (each split element is a copy).
Pre-auth HTTP DoS.

### Root cause

```python
parts = data[:final_boundary_index].split(b"--" + boundary + b"\r\n")  # :34  huge list first
if len(parts) > config.max_parts:                                       # :35  check after
    raise HTTPInputError("multipart/form-data has too many parts")
```

### PoC

gist: https://gist.github.com/afldl/649861f25d39b53b7edbe0298e171617
`poc.py` + `output.txt` (100k parts from 600KB   transient list).

### Fix

Count separators without materializing the list (e.g. `data.count(b"--"+boundary)` first).

### Credit

Reported by afldl, 2026-07.

## References
- https://github.com/tornadoweb/tornado/security/advisories/GHSA-8423-8fgw-73vq
- https://github.com/tornadoweb/tornado/pull/3704
- https://github.com/tornadoweb/tornado/commit/de85b3f87446e323e881bbaa3d5a74f4b76e5f05
- https://gist.github.com/afldl/649861f25d39b53b7edbe0298e171617
- https://github.com/tornadoweb/tornado
- https://github.com/tornadoweb/tornado/releases/tag/v6.5.8
