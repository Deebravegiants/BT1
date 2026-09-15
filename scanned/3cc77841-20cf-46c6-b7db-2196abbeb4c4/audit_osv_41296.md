# [C] Apache Airflow FAB provider: FAB auth manager: JWT signature verification disabled by default for Azure AD OAuth (`verify_signature` defaults to `False`)

## Summary
Severity: Critical
Advisory: CVE-2026-59243
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-59243
Type: osv

## Details
The FAB auth manager's Azure AD OAuth login defaulted `verify_signature=False` when decoding the ID token, so an attacker able to present a forged or unsigned (`alg:none`) ID token to the OAuth callback could bypass authentication and log in as an arbitrary user, including one holding the Admin role (CWE-347). Deployments running the FAB auth manager with the Azure AD OAuth login path under its default configuration are affected; the Authentik path already defaulted to `True`. This issue affects `apache-airflow-providers-fab` before 3.7.3. Users are advised to upgrade to `apache-airflow-providers-fab` 3.7.3, which defaults `verify_signature=True`.

## References
- http://www.openwall.com/lists/oss-security/2026/07/28/10
- https://pypi.python.org
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/59xxx/CVE-2026-59243.json
- https://lists.apache.org/thread/x4784l7z00tl3gw4tv2dmvoon77rxgpl
- https://nvd.nist.gov/vuln/detail/CVE-2026-59243
- https://github.com/apache/airflow/pull/69374
