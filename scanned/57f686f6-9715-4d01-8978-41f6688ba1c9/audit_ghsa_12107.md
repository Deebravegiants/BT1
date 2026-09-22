# [M] Unauthenticated SSRF Vulnerability in Streamlit on Windows (NTLM Credential Exposure)

## Summary
Severity: Medium
Advisory: GHSA-7p48-42j8-8846
CVE: CVE-2026-33682
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-7p48-42j8-8846
Type: github-advisory

## Affected
- PyPI: `Streamlit` — affected >=0 <1.54.0

## Details
# Streamlit Open Source Security Advisory

## 1. Impacted Products

Streamlit Open Source versions prior to 1.54.0 running on Windows hosts.

## 2. Introduction

Snowflake Streamlit Open Source addressed a security vulnerability affecting Windows deployments related to improper handling and validation of filesystem paths within component request handling. The vulnerability was reported through the responsible disclosure program and has been remediated in Streamlit Open Source version 1.54.0. This issue affects only Streamlit deployments running on Windows operating systems.

## 3. Server-Side Request Forgery (SSRF) and NTLM Credential Exposure

### 3.1 Description

Streamlit was informed by a security researcher of an unauthenticated Server-Side Request Forgery (SSRF) vulnerability. The vulnerability arises from improper validation of attacker-supplied filesystem paths. In certain code paths, including within the `ComponentRequestHandler`, filesystem paths are resolved using `os.path.realpath()` or `Path.resolve()` before sufficient validation occurs.

On Windows systems, supplying a malicious UNC path (e.g., `\\attacker-controlled-host\share`) can cause the Streamlit server to initiate outbound SMB connections over port 445. When Windows attempts to authenticate to the remote SMB server, NTLMv2 challenge-response credentials of the Windows user running the Streamlit process may be transmitted.

This behavior may allow an attacker to:

- Perform NTLM relay attacks against other internal services
- Identify internally reachable SMB hosts via timing analysis

> **Note:** The issue is unauthenticated and does not require user interaction.

Captured NTLMv2 challenge-response hashes could be subjected to offline brute-force attacks in an attempt to recover the associated plaintext account password. While NTLMv2 incorporates a server challenge (nonce) that mitigates the use of precomputed rainbow tables, it does not prevent targeted offline password cracking against weak credentials.

Additionally, Microsoft has publicly discouraged the continued use of NTLM in favor of Kerberos and is actively progressing toward disabling NTLM by default in future Windows releases. Organizations that enforce NTLM restrictions, disable outbound NTLM authentication, require SMB signing, or block NTLM authentication to remote servers can reduce or eliminate the risk associated with credential relay or hash exposure scenarios.

As NTLM is considered legacy and increasingly deprecated (though not fully sunset), environments that have already implemented Microsoft-recommended NTLM hardening controls are less likely to be materially impacted. The overall risk therefore depends on the organization's authentication configuration and network security posture.

### 3.2 Scenarios and Attack Vectors

Streamlit applications running on Windows were vulnerable if component endpoints were exposed to untrusted networks. By appending an attacker-controlled SMB hostname to the URI path and issuing a GET request, the Streamlit server could be coerced into initiating an outbound SMB authentication attempt.

This could result in the leakage of NTLMv2 credential hashes for the Windows account running the Streamlit process.

### 3.3 Resolution

- The vulnerability has been fixed in Streamlit Open Source version 1.54.0.
- It is recommended that all Streamlit deployments on Windows be upgraded immediately to version 1.54.0 or later.

## 4. Contact

Please contact [security@snowflake.com](mailto:security@snowflake.com) for any questions regarding this advisory.

If a security vulnerability is discovered in a Streamlit product or website, it should be reported through the responsible disclosure program. For more information, see the [Vulnerability Disclosure Policy](https://hackerone.com/snowflake).

## References
- https://github.com/streamlit/streamlit/security/advisories/GHSA-7p48-42j8-8846
- https://nvd.nist.gov/vuln/detail/CVE-2026-33682
- https://github.com/streamlit/streamlit/commit/23692ca70b2f2ac720c72d1feb4f190c9d6eed76
- https://github.com/streamlit/streamlit
- https://github.com/streamlit/streamlit/releases/tag/1.54.0
