# [M] Path traveral in Streamlit on windows

## Summary
Severity: Medium
Advisory: GHSA-rxff-vr5r-8cj5
CVE: CVE-2024-42474
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-08-12
Source: https://github.com/advisories/GHSA-rxff-vr5r-8cj5
Type: github-advisory

## Affected
- PyPI: `streamlit` — affected >=0 <1.37.0

## Details
### 1. Impacted Products
Streamilt Open Source versions before 1.37.0.

### 2. Introduction
Snowflake Streamlit open source addressed a security vulnerability via the [static file sharing feature](https://docs.streamlit.io/develop/concepts/configuration/serving-static-files). The vulnerability was patched on Jul 25, 2024, as part of Streamlit open source version 1.37.0. The vulnerability only affects Windows.

### 3. Path Traversal Vulnerability 
#### 3.1 Description
On May 12, 2024, Streamlit was informed via our bug bounty program about a path traversal vulnerability in the open source library. We fixed and merged a patch remediating the vulnerability on Jul 25, 2024. The issue was determined to be in the moderate severity range with a maximum CVSSv3 base score of [5.9](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N)
#### 3.2 Scenarios and attack vector(s)
Users of hosted Streamlit app(s) on Windows were vulnerable to a path traversal vulnerability when the [static file sharing feature](https://docs.streamlit.io/develop/concepts/configuration/serving-static-files) is enabled. An attacker could utilize the vulnerability to leak the password hash of the Windows user running Streamlit. 
#### 3.3 Resolution
The vulnerability has been fixed in all Streamlit versions released since Jul 25, 2024. We recommend all users upgrade to Version 1.37.0.

### 4. Contact
Please contact security@snowflake.com if you have any questions regarding this advisory. If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne. For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/streamlit/streamlit/security/advisories/GHSA-rxff-vr5r-8cj5
- https://nvd.nist.gov/vuln/detail/CVE-2024-42474
- https://github.com/streamlit/streamlit/commit/3a639859cfdfba2187c81897d44a3e33825eb0a3
- https://github.com/pypa/advisory-database/tree/main/vulns/streamlit/PYSEC-2024-153.yaml
- https://github.com/streamlit/streamlit
