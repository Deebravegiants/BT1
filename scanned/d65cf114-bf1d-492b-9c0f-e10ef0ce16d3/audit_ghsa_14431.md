# [M] Streamlit publishes previously-patched Cross-site Scripting vulnerability

## Summary
Severity: Medium
Advisory: GHSA-9c6g-qpgj-rvxw
CVE: CVE-2023-27494
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-9c6g-qpgj-rvxw
Type: github-advisory

## Affected
- PyPI: `streamlit` — affected >=0.63.0 <0.81.0

## Details
**Synopsis:**  Streamlit open source publicizes a prior security fix implemented in 2021. The vulnerability affected Streamlit versions between 0.63.0 and 0.80.0 (inclusive) and was patched on April 21, 2021.  If you are using Streamlit with version before 0.63.0 or after 0.80.0, no action is required. 
# 1. Impacted Products
Streamilt Open Source versions between 0.63.0 and 0.80.0.
# 2. Introduction
On April 21, 2021, Streamlit merged a patch that fixed a cross-site scripting (XSS) vulnerability in the Streamlit open source library, without an associated public advisory.  The vulnerability affected Streamlit versions between 0.63.0 and 0.80.0 (inclusive), which are no longer supported. We recommend using the latest version of our library, but so long as you are not using an affected Streamlit version, no action is required. 
# 3. Cross Site Scripting Vulnerability 
## 3.1 Description
On April 20, 2021, Streamlit was informed via our support forum about a XSS vulnerability in the open source library. We fixed and merged a patch remediating the vulnerability on April 21st, 2021. The issue was determined to be in the moderate severity range with a maximum CVSSv3 base score of [5.9](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:L/A:N)
## 3.2 Scenarios and attack vector(s)
Users of hosted Streamlit app(s) were vulnerable to a reflected XSS vulnerability. An attacker could craft a malicious URL with Javascript payloads to a Streamlit app. The attacker could then trick the user into visiting the malicious URL and, if successful, the server would render the malicious javascript payload as-is, leading to an XSS. 
## 3.3 Our response
Streamlit fixed and merged a patch for this vulnerability on April 21, 2021. The vulnerability was fixed within 24hrs of notification to Streamlit. 
## 3.4 Resolution
The vulnerability has been fixed in all Streamlit versions released since April 21, 2021.  The affected versions – those between 0.63.0 and 0.80.0 (inclusive) – are no longer supported. We recommend always using supported versions of the Streamlit open source library. Version 1.19.0 is current as of this advisory. 
# 4. Contact
Please contact security@snowflake.com if you have any questions regarding this advisory. If you discover a security vulnerability in one of our products or websites, please report the issue to HackerOne.  For more information, please see our [Vulnerability Disclosure Policy](https://hackerone.com/snowflake?type=team).

## References
- https://github.com/streamlit/streamlit/security/advisories/GHSA-9c6g-qpgj-rvxw
- https://nvd.nist.gov/vuln/detail/CVE-2023-27494
- https://github.com/streamlit/streamlit/commit/afcf880c60e5d7538936cc2d9721b9e1bc02b075
- https://github.com/pypa/advisory-database/tree/main/vulns/streamlit/PYSEC-2023-50.yaml
- https://github.com/streamlit/streamlit
