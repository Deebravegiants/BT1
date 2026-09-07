# [H] amazon-braket-sdk vulnerable to Insecure Deserialization via pickle.loads()

## Summary
Severity: High
Advisory: GHSA-g697-2xrc-gc46
CVE: CVE-2026-9291
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-g697-2xrc-gc46
Type: github-advisory

## Affected
- PyPI: `amazon-braket-sdk` — affected >=1.10.0 <1.117.0

## Details
**Summary**
Amazon Braket SDK is an open-source Python library for interacting with the Amazon Braket quantum computing service, including managing hybrid quantum jobs and retrieving job results. An issue exists where, under certain circumstances, a remote authenticated user with S3 write access to a Braket job output bucket can achieve arbitrary code execution by exploiting insecure deserialization in the job results processing component.

**Impact**
The SDK's deserialize_values() function reads the dataFormat field directly from the job results JSON file without validation. An actor with write access to the victim's S3 job output bucket can modify the dataFormat field in results.json from PLAINTEXT to pickled_v4 and replace dataDictionary values with base64-encoded executable payloads. When the victim calls job.result(), load_job_result(), or load_job_checkpoint() as part of their normal Braket workflow, the SDK calls pickle.loads() on the actor-controlled data, executing arbitrary code with the victim's permissions.

**Impacted versions**: >= v1.10.0 AND < 1.117.0

**Patches**
This issue has been addressed in amazon-braket-sdk version 1.117.0. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

**Workarounds**
If users cannot upgrade immediately:

1. Restrict S3 bucket policies on the Braket job output buckets to enforce least-privilege access, ensuring only trusted principals have s3:PutObject permissions. This limits an an actor's ability to plant an executable payload.
2. Validate the dataFormat field in job result metadata before calling job.result(). Refuse to process results where the format is pickled_v4 if it did not explicitly configure pickle serialization.

**References**
If users have any questions or comments about this advisory, amazon-braket-sdk asks that users contact AWS Security via the [vulnerability reporting page](https://aws.amazon.com/security/vulnerability-reporting) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/amazon-braket/amazon-braket-sdk-python/security/advisories/GHSA-g697-2xrc-gc46
- https://nvd.nist.gov/vuln/detail/CVE-2026-9291
- https://aws.amazon.com/security/security-bulletins/2026-036-aws
- https://github.com/amazon-braket/amazon-braket-sdk-python
- https://github.com/amazon-braket/amazon-braket-sdk-python/releases/tag/v1.117.0
