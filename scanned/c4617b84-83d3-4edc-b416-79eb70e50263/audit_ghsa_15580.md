# [M] Indico has a Cross-Site-Scripting during account creation

## Summary
Severity: Medium
Advisory: GHSA-rrqf-w74j-24ff
CVE: CVE-2024-45399
CWE: CWE-1395, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-04
Source: https://github.com/advisories/GHSA-rrqf-w74j-24ff
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <3.3.4

## Details
### Impact
There is a Cross-Site-Scripting vulnerability during account creation when redirecting after the account has been successfully created.
Exploitation requires the user to initiate the account creation process with a maliciously crafted link, and then finalize the signup process. Because of this, it can only target newly created (and thus unprivileged) Indico users so the benefits of exploiting it are very limited.

### Patches
You should to update to [Indico 3.3.4](https://github.com/indico/indico/releases/tag/v3.3.4) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
- If you build the Indico package yourself and cannot upgrade for some reason, you can simply update the `flask-multipass` dependency to `>=0.5.5` which fixes the vulnerability. You would do that by editing `requirements.txt` before building the package (see commit 7dcb573837), or possibly cherry-picking that particular commit.
- Otherwise you could configure your web server to disallow requests containing a query string with a parameter that starts with `javascript:`

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at [indico-team@cern.ch](mailto:indico-team@cern.ch)

## References
- https://github.com/indico/indico/security/advisories/GHSA-rrqf-w74j-24ff
- https://nvd.nist.gov/vuln/detail/CVE-2024-45399
- https://github.com/indico/flask-multipass/commit/0bdcf656d469e5f675cb56fd644d82fea3a97c2a
- https://github.com/indico/indico/commit/7dcb573837b9fd09d95f74d1baeae225b164cc8f
- https://github.com/indico/indico
- https://github.com/indico/indico/releases/tag/v3.3.4
- https://github.com/pypa/advisory-database/tree/main/vulns/indico/PYSEC-2024-90.yaml
