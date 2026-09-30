# [M] Indico vulnerability allows attackers to bulk dump user details

## Summary
Severity: Medium
Advisory: GHSA-q28v-664f-q6wj
CVE: CVE-2025-53640
CWE: CWE-200, CWE-639, CWE-862
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2025-07-14
Source: https://github.com/advisories/GHSA-q28v-664f-q6wj
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=2.2 <3.3.7

## Details
### Impact
An endpoint used to display details of users listed in certain fields (such as ACLs) could be misused to dump basic user details (such as name, affiliation and email) in bulk.

> [!TIP]
> If your instance allows everyone to create a user account, and you wish to truly restrict access to these user details, consider restricting user search to managers. You can find details on the newly introduced indico.conf setting [`ALLOW_PUBLIC_USER_SEARCH`](https://docs.getindico.io/en/stable/config/settings/#ALLOW_PUBLIC_USER_SEARCH) in our documentation.

### Patches
You should to update to [Indico 3.3.7](https://github.com/indico/indico/releases/tag/v3.3.7) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
It is possible to restrict access to the affected endpoints (e.g. in the webserver config), but doing so would break certain form fields which could no longer show the details of the users listed in those fields, so upgrading instead is highly recommended.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

#### Credits
This vulnerability was identified during a security assessment conducted as part of the Red Team Residency Program at RNP (Rede Nacional de Ensino e Pesquisa).
The research and testing were performed by a security researcher working under RNP’s authorization and coordination.
Special acknowledgment goes to the RNP Security Team, which provided the infrastructure, methodology, and ethical oversight for this work.

## References
- https://github.com/indico/indico/security/advisories/GHSA-q28v-664f-q6wj
- https://nvd.nist.gov/vuln/detail/CVE-2025-53640
- https://github.com/indico/indico/pull/6936/commits/f8583557a3da56aeea8857ae69bf17c9066c95c1
- https://docs.getindico.io/en/stable/config/settings/#ALLOW_PUBLIC_USER_SEARCH
- https://docs.getindico.io/en/stable/installation/upgrade
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.7
- https://www.vicarius.io/vsociety/posts/cve202553640-detect-indico-vulnerability
- https://www.vicarius.io/vsociety/posts/cve202553640-mitigate-indico-vulnerability
