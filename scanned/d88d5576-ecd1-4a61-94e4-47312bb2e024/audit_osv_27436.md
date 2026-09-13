# [H] CVE-2024-21513

## Summary
Severity: High
Advisory: CVE-2024-21513
Aliases: GHSA-cgcg-p68q-3w7v, PYSEC-2024-62
CVSS: 8.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H/E:P)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/CVE-2024-21513
Type: osv

## Details
Versions of the package langchain-experimental from 0.0.15 and before 0.0.21 are vulnerable to Arbitrary Code Execution when retrieving values from the database, the code will attempt to call 'eval' on all values. An attacker can exploit this vulnerability and execute arbitrary python code if they can control the input prompt and the server is configured with VectorSQLDatabaseChain.**Notes:**Impact on the Confidentiality, Integrity and Availability of the vulnerable component:Confidentiality: Code execution happens within the impacted component, in this case langchain-experimental, so all resources are necessarily accessible.Integrity: There is nothing protected by the impacted component inherently. Although anything returned from the component counts as 'information' for which the trustworthiness can be compromised.Availability: The loss of availability isn't caused by the attack itself, but it happens as a result during the attacker's post-exploitation steps.Impact on the Confidentiality, Integrity and Availability of the subsequent system:As a legitimate low-privileged user of the package (PR:L) the attacker does not have more access to data owned by the package as a result of this vulnerability than they did with normal usage (e.g. can query the DB). The unintended action that one can perform by breaking out of the app environment and exfiltrating files, making remote connections etc. happens during the post exploitation phase in the subsequent system - in this case, the OS.AT:P: An attacker needs to be able to influence the input prompt, whilst the server is configured with the VectorSQLDatabaseChain plugin.

## References
- https://github.com/langchain-ai/langchain/blob/672907bbbb7c38bf19787b78e4ffd7c8a9026fe4/libs/experimental/langchain_experimental/sql/vector_sql.py%23L81
- https://security.snyk.io/vuln/SNYK-PYTHON-LANGCHAINEXPERIMENTAL-7278171
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21513.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21513
- https://github.com/langchain-ai/langchain/commit/7b13292e3544b2f5f2bfb8a27a062ea2b0c34561
