# [H] Indico Tampering with links (e.g. password reset) in sent emails

## Summary
Severity: High
Advisory: GHSA-wgpj-7c2j-vfjm
CVE: CVE-2021-30185
CWE: CWE-640
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-04-08
Source: https://github.com/advisories/GHSA-wgpj-7c2j-vfjm
Type: github-advisory

## Affected
- PyPI: `indico` — affected >=0 <2.3.4

## Details
### Impact
An external audit of the Indico codebase has discovered a vulnerability in Indico's URL generation logic which could have allowed an attacker to make Indico send a password reset link with a valid token pointing to an attacker-controlled domain by sending that domain in the `Host` header. Had a user clicked such a link without realizing it does not point to Indico (and that they never requested it), it would have revealed their password reset token to the attacker, allowing them to reset the password for that user and thus take over their Indico account.

- If the web server already enforces a canonical host name, this cannot be exploited (this was not part of the default config from the Indico setup guide)
- If only SSO is used ([`LOCAL_IDENTITIES`](https://docs.getindico.io/en/stable/config/settings/#LOCAL_IDENTITIES) set to `False`), the vulnerability cannot be exploited for password reset links, but other links in emails set by Indico could be tampered with in the same way (with less problematic impact though)

### Patches
You need to update to [Indico 2.3.4](https://github.com/indico/indico/releases/tag/v2.3.4) as soon as possible.
See [the docs](https://docs.getindico.io/en/stable/installation/upgrade/) for instructions on how to update.

### Workarounds
You can configure the web server to canonicalize the URL to the hostname used for Indico. See [this commit](https://github.com/indico/indico/pull/4815/commits/b6bff6d004abcf07db1891e26a0eb4aa0edb7c21) for the changes in our setup docs; they can be easily applied to your existing web server config.

### For more information
If you have any questions or comments about this advisory:

- Open a thread in [our forum](https://talk.getindico.io/)
- Email us privately at indico-team@cern.ch

## References
- https://github.com/indico/indico/security/advisories/GHSA-wgpj-7c2j-vfjm
- https://nvd.nist.gov/vuln/detail/CVE-2021-30185
- https://github.com/advisories/GHSA-wgpj-7c2j-vfjm
- https://github.com/indico/indico/releases/tag/v2.3.4
- https://github.com/pypa/advisory-database/tree/main/vulns/indico/PYSEC-2021-18.yaml
- https://www.shorebreaksecurity.com/blog
