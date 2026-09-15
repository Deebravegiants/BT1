# [H] sagemaker-python-sdk vulnerable to Deserialization of Untrusted Data

## Summary
Severity: High
Advisory: GHSA-wjvx-jhpj-r54r
CVE: CVE-2024-34072
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-03
Source: https://github.com/advisories/GHSA-wjvx-jhpj-r54r
Type: github-advisory

## Affected
- PyPI: `sagemaker` — affected >=0 <2.218.0

## Details
### Impact

sagemaker.base_deserializers.NumpyDeserializer module before v2.218.0 allows potentially unsafe deserialization when untrusted data is passed as pickled object arrays. This consequently may allow an unprivileged third party to cause remote code execution, denial of service, affecting both confidentiality and integrity.

Impacted versions: <2.218.0.

### Credit 

We would like to thank HiddenLayer for collaborating on this issue through the coordinated vulnerability disclosure process.


### Workarounds

Do not pass pickled numpy object arrays which originated from an untrusted source, or that could have been tampered with. Only pass pickled numpy object arrays from sources you trust.


### References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.
[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

Fixed by: [https://github.com/aws/sagemaker-python-sdk/pull/4557](https://github.com/aws/sagemaker-python-sdk/pull/4557)

## References
- https://github.com/aws/sagemaker-python-sdk/security/advisories/GHSA-wjvx-jhpj-r54r
- https://nvd.nist.gov/vuln/detail/CVE-2024-34072
- https://github.com/aws/sagemaker-python-sdk/pull/4557
- https://github.com/aws/sagemaker-python-sdk/commit/72e0c9712aec6fbb82fb40fda091dfc2a42c70a0
- https://github.com/aws/sagemaker-python-sdk
