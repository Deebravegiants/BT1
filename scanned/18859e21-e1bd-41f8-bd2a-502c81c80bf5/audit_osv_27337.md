# [M] LangChain langchain_community TFIDFRetriever tfidf.py load_local server-side request forgery

## Summary
Severity: Medium
Advisory: CVE-2024-2057
Aliases: PYSEC-2024-278
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2024-2057
Type: osv

## Details
A vulnerability was found in LangChain langchain_community 0.0.26. It has been classified as critical. Affected is the function load_local in the library libs/community/langchain_community/retrievers/tfidf.py of the component TFIDFRetriever. The manipulation leads to server-side request forgery. It is possible to launch the attack remotely. The exploit has been disclosed to the public and may be used. Upgrading to version 0.0.27 is able to address this issue. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-255372.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/2xxx/CVE-2024-2057.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-2057
- https://vuldb.com/?id.255372
- https://vuldb.com/?ctiid.255372
- https://github.com/langchain-ai/langchain/pull/18695
- https://github.com/bayuncao/vul-cve-16
- https://github.com/bayuncao/vul-cve-16/tree/main/PoC.pkl
