# [C] CVE-2020-15208

## Summary
Severity: Critical
Advisory: CVE-2020-15208
Aliases: BIT-tensorflow-2020-15208, GHSA-mxjj-953w-2c2v, PYSEC-2020-131, PYSEC-2020-288, PYSEC-2020-323
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-09-25
Source: https://osv.dev/vulnerability/CVE-2020-15208
Type: osv

## Details
In tensorflow-lite before versions 1.15.4, 2.0.3, 2.1.2, 2.2.1 and 2.3.1, when determining the common dimension size of two tensors, TFLite uses a `DCHECK` which is no-op outside of debug compilation modes. Since the function always returns the dimension of the first tensor, malicious attackers can craft cases where this is larger than that of the second tensor. In turn, this would result in reads/writes outside of bounds since the interpreter will wrongly assume that there is enough data in both tensors. The issue is patched in commit 8ee24e7949a203d234489f9da2c5bf45a7d5157d, and is released in TensorFlow versions 1.15.4, 2.0.3, 2.1.2, 2.2.1, or 2.3.1.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00065.html
- https://github.com/tensorflow/tensorflow/releases/tag/v2.3.1
- https://github.com/tensorflow/tensorflow/commit/8ee24e7949a203d234489f9da2c5bf45a7d5157d
- https://github.com/tensorflow/tensorflow/security/advisories/GHSA-mxjj-953w-2c2v
