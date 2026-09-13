# [H] Thumbor convolution filter allows divide-by-zero in C extension leading to remote DoS

## Summary
Severity: High
Advisory: GHSA-cqjp-jf4r-h5q9
CVE: CVE-2026-53503
CWE: CWE-20, CWE-369
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-31
Source: https://github.com/advisories/GHSA-cqjp-jf4r-h5q9
Type: github-advisory

## Affected
- PyPI: `thumbor` — affected >=0 <7.8.0

## Details
### Summary
Thumbor's `filters:convolution(<matrix>, <columns>, <should_normalize>)` filter passes the user-controlled `<columns>` value to a C extension (`thumbor/ext/filters/_convolution.c`) where it is used as a divisor (for `%` and `/`) without validating `columns > 0`. When `columns=0`, the C code triggers undefined behavior; on x86_64 this reliably results in a fatal divide-by-zero trap (SIGFPE) and crashes the Thumbor process (confirmed on Linux x86_64 and macOS Intel x86_64), causing a remote denial of service.

### Details
#### Root cause
The Python filter accepts `columns=0`, and the native C extension uses `columns_count` as a divisor without validating it.

1) Python filter entry point allows `columns=0` (`thumbor/filters/convolution.py`):
```python
@filter_method(
    r"(?:[-]?[\d]+\.?[\d]*[;])*(?:[-]?[\d]+\.?[\d]*)",
    BaseFilter.PositiveNumber,  # accepts 0
    BaseFilter.Boolean,
)
async def convolution(self, matrix, columns, should_normalize=True):
    ...
    imgdata = _convolution.apply(..., matrix, columns, should_normalize)
```
`BaseFilter.PositiveNumber` matches `"0"` (`thumbor/filters/__init__.py`):
```python
class BaseFilter:
    PositiveNumber = {"regex": r"[\d]+", "parse": int}  # matches "0"
    PositiveNonZeroNumber = {"regex": r"[\d]*[1-9][\d]*", "parse": int}
```

2) C extension divides/modulos by `columns_count` without a zero check (`thumbor/ext/filters/_convolution.c`):
```c
kernel_size = PyTuple_Size(kernel_tuple);
if ((kernel_size % columns_count != 0) ||
    (kernel_size % 2 == 0) ||
    ((kernel_size / columns_count) % 2) == 0) {
    // TODO: error, not a valid kernel
    return NULL;
}
```


### PoC
#### Test environment
- Linux x86_64

#### Preconditions
- The `convolution` filter is enabled (it is enabled by default via `BUILTIN_FILTERS`).
- Either:
  - `/unsafe/` URLs are allowed (`ALLOW_UNSAFE_URL=True`), OR
  - `/unsafe/` is disabled, and the attacker has a valid signed URL (i.e., the attacker is an authorized user/partner, or can obtain signed URLs from a trusted signing service).

#### Example request (signed URL)
`http://<host>:<port>/<url-sign>/400x400/filters:convolution(1;2;1;2;4;2;1;2;1,0,true)/example.jpg`

#### Example request (/unsafe/)
`http://<host>:<port>/unsafe/400x400/filters:convolution(1;2;1;2;4;2;1;2;1,0,true)/example.jpg`


### Impact
- Remote Denial of Service via process crash (SIGFPE) on x86_64 (confirmed on Linux x86_64 and macOS Intel x86_64).
- Exploitability depends on deployment:
  - If `/unsafe/` is enabled: unauthenticated remote DoS.
  - If `/unsafe/` is disabled: the attacker needs a valid signed URL.(i.e., the attacker is an authorized user/partner, or can obtain signed URLs from a trusted signing service)


### Suggested remediation
- In the C extension (`thumbor/ext/filters/_convolution.c`):
  - Reject `columns_count <= 0` before any `%` or `/`.
- In the Python filter (`thumbor/filters/convolution.py`):
  - Require `columns` to be non-zero (e.g., use `BaseFilter.PositiveNonZeroNumber`).

## References
- https://github.com/thumbor/thumbor/security/advisories/GHSA-cqjp-jf4r-h5q9
- https://github.com/thumbor/thumbor/commit/447e192e3fb92e64c12e5354a56a4a7133f69d73
- https://github.com/thumbor/thumbor
- https://github.com/thumbor/thumbor/releases/tag/7.8.0
