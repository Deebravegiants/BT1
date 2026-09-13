# [H] curl_cffi bundles a version of libcurl affected by High Severity vulnerability

## Summary
Severity: High
Advisory: GHSA-3vpc-4p9p-47hc
CWE: CWE-1395
Ecosystem: PyPI
Published: 2024-10-22
Source: https://github.com/advisories/GHSA-3vpc-4p9p-47hc
Type: github-advisory

## Affected
- PyPI: `curl-cffi` — affected >=0 <0.7.0b6

## Details
### Summary
curl_cffi is potentially affected by High Severity vulnerability (CVE-2023-38545) in libcurl<8.4.0

### Details
HIGH severity vulnerability in curl and libcurl: [announcement](https://github.com/curl/curl/discussions/12026#discussioncomment-7195548)
Details are still unknown, but seems it will be a major issue as it's advertised by curl devs as "_probably the worst curl security flaw in a long time_".
A patched version (8.4.0) and details will be published around 06:00 UTC on October 11.
curl_cffi wheels on PyPI ship with libcurl 7.84.0

### PoC
[https://inspector.pypi.io/project/curl-cffi/0.5.10b2/packages/56/ae/eb7d39ad234f1f44650b910757d5aa696feff413d327c8328223ce78cb76/curl_cffi-0.5.10b2-cp37-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl/curl_cffi/include/curl/curlver.h](https://inspector.pypi.io/project/curl-cffi/0.5.10b2/packages/56/ae/eb7d39ad234f1f44650b910757d5aa696feff413d327c8328223ce78cb76/curl_cffi-0.5.10b2-cp37-abi3-manylinux_2_17_aarch64.manylinux2014_aarch64.whl/curl_cffi/include/curl/curlver.h)

### Resolution

Versions after 0.7 bundles with `libcurl>=8.5`, which is not affected by this issue.

## References
- https://github.com/lexiforest/curl_cffi/security/advisories/GHSA-3vpc-4p9p-47hc
- https://github.com/advisories/GHSA-7xw9-w465-6x42
- https://github.com/lexiforest/curl_cffi
