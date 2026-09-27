# [H] CVE-2026-13444

## Summary
Severity: High
Advisory: CVE-2026-13444
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-13444
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.1 can allow an attacker to access another user's private vector documents by creating their own flow with matching Chroma persist_directory and collection_name values. The attacker receives exact victim content in their workflow output despite having no authorization to read the victim's flow. Additionally, the attacker can pollute the victim's collection by inserting their own documents into the shared namespace.

## References
- https://www.ibm.com/support/pages/node/7279989
