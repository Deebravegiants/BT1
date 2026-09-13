# [H] Integer truncation in Shard API usage

## Summary
Severity: High
Advisory: GHSA-h6fg-mjxg-hqq4
CVE: CVE-2020-15202
CWE: CWE-197, CWE-754
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-25
Source: https://github.com/advisories/GHSA-h6fg-mjxg-hqq4
Type: github-advisory

## Affected
- PyPI: `tensorflow` — affected >=0 <1.15.4
- PyPI: `tensorflow` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-cpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-cpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-cpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-cpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-cpu` — affected >=2.3.0 <2.3.1
- PyPI: `tensorflow-gpu` — affected >=0 <1.15.4
- PyPI: `tensorflow-gpu` — affected >=2.0.0 <2.0.3
- PyPI: `tensorflow-gpu` — affected >=2.1.0 <2.1.2
- PyPI: `tensorflow-gpu` — affected >=2.2.0 <2.2.1
- PyPI: `tensorflow-gpu` — affected >=2.3.0 <2.3.1

## Details
### Impact
The `Shard` API in TensorFlow expects the last argument to be a function taking two `int64` (i.e., `long long`) arguments:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/util/work_sharder.h#L59-L60

However, there are several places in TensorFlow where a lambda taking `int` or `int32` arguments is being used:
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/random_op.cc#L204-L205
https://github.com/tensorflow/tensorflow/blob/0e68f4d3295eb0281a517c3662f6698992b7b2cf/tensorflow/core/kernels/random_op.cc#L317-L318

In these cases, if the amount of work to be parallelized is large enough, integer truncation occurs. Depending on how the two arguments of the lambda are used, this can result in segfaults, read/write outside of heap allocated arrays, stack overflows, or data corruption.

### Patches
We have patched the issue in 27b417360cbd671ef55915e4bb6bb06af8b8a832 and ca8c013b5e97b1373b3bb1c97ea655e69f31a575. We will release patch releases for all versions between 1.15 and 2.3.

We recommend users to upgrade to TensorFlow 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

### For more information
Please consult [our security guide](https://github.com/tensorflow/tensorflow/blob/master/SECURITY.md) for more information regarding the security model and how to contact us with issues and questions.

### Attribution
This vulnerability has been reported by members of the Aivul Team from Qihoo 360.

## References
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-h6fg-mjxg-hqq4
- https://nvd.nist.gov/vuln/detail/CVE-2020-15202
- https://github.com/tensorflow/tensorflow/commit/27b417360cbd671ef55915e4bb6bb06af8b8a832
- https://github.com/tensorflow/tensorflow/commit/ca8c013b5e97b1373b3bb1c97ea655e69f31a575
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-cpu/PYSEC-2020-282.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow-gpu/PYSEC-2020-317.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/tensorflow/PYSEC-2020-125.yaml
- https://github.com/tensorflow/tensorflow
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
