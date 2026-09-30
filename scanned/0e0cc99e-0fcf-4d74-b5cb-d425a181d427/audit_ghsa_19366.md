# [H] Issue with Amazon Redshift Python Connector and the BrowserAzureOAuth2CredentialsProvider plugin

## Summary
Severity: High
Advisory: GHSA-r244-wg5g-6w2r
CVE: CVE-2025-5279
CWE: CWE-295
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-r244-wg5g-6w2r
Type: github-advisory

## Affected
- PyPI: `redshift-connector` — affected >=2.0.872 <2.1.7

## Details
### Summary
[Amazon Redshift Python Connector](https://docs.aws.amazon.com/redshift/latest/mgmt/python-redshift-driver.html) is a pure Python connector to Redshift (i.e., driver) that implements the [Python Database API Specification 2.0](https://www.python.org/dev/peps/pep-0249/).

When the Amazon Redshift Python Connector is configured with the BrowserAzureOAuth2CredentialsProvider plugin, the driver skips the SSL certificate validation step for the Identity Provider. 

### Impact

An insecure connection could allow an actor to intercept the token exchange process and retrieve an access token.

**Impacted versions:** >=2.0.872;<=2.1.6

### Patches

Upgrade Amazon Redshift Python Connector to version 2.1.7 and ensure any forked or derivative code is patched to incorporate the new fixes.

### Workarounds

None

### References

If you have any questions or comments about this advisory we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] Vulnerability reporting page: https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/aws/amazon-redshift-python-driver/security/advisories/GHSA-r244-wg5g-6w2r
- https://nvd.nist.gov/vuln/detail/CVE-2025-5279
- https://aws.amazon.com/security/security-bulletins
- https://aws.amazon.com/security/security-bulletins/AWS-2025-011
- https://github.com/aws/amazon-redshift-python-driver
- https://github.com/aws/amazon-redshift-python-driver/releases/tag/v2.1.7
