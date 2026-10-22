# [M] vault-cli contains possible RCE when reading user-defined data

## Summary
Severity: Medium
Advisory: GHSA-q34h-97wf-8r8j
CVE: CVE-2021-43837
CWE: CWE-74, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-12-16
Source: https://github.com/advisories/GHSA-q34h-97wf-8r8j
Type: github-advisory

## Affected
- PyPI: `vault-cli` — affected >=0.7.0 <3.0.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

vault-cli features the ability for rendering templated values (as explained in the [documentation](https://github.com/peopledoc/vault-cli/blob/2.2.1/docs/howto/templated_secrets.rst)). When a secret starts with the prefix `!template!`, vault-cli interprets the rest of the contents of the secret as a Jinja2 template.
Jinja2 is a powerful templating engine and it's not designed to safely render arbitrary templates. An attacker controlling a jinja2 template rendered on a machine can trigger arbitrary code, making this a Remote Code Execution (RCE) risk.
If the content of the vault can be completely trusted, then this is not a problem. Otherwise, if your threat model includes cases where an attacker can manipulate a secret value read from the vault using vault-cli, then this vulnerability may impact you.

This does not impact `vault` itself, except for the fact that the attacker, having an RCE on the machine that executes `vault-cli`, may abuse the token that `vault-cli` uses, to read, write or delete other data from the vault.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

In 3.0.0, the code related to interpreting vault templated secrets has been removed entirely.

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

Using the environment variable `VAULT_CLI_RENDER=false` or the flag `--no-render` (placed between `vault-cli` and the subcommand, e.g. `vault-cli --no-render get-all`) or adding `render: false` to the vault-cli configuration yaml file disables rendering and removes the vulnerability.
Using the python library, you can use: `vault_cli.get_client(render=False)` when creating your client to get a client that will not render templated secrets and thus operates securely.

### References
_Are there any links users can visit to find out more?_

Here's an article explaining how jinja2 templates might be exploited to have side effects: https://podalirius.net/en/publications/grehack-2021-optimizing-ssti-payloads-for-jinja2/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the vault-cli repo](https://github.com/peopledoc/vault-cli/issues/new)

## References
- https://github.com/peopledoc/vault-cli/security/advisories/GHSA-q34h-97wf-8r8j
- https://nvd.nist.gov/vuln/detail/CVE-2021-43837
- https://github.com/peopledoc/vault-cli/pull/198
- https://github.com/peopledoc/vault-cli/commit/3ba3955887fd6b7d4d646c8b260f21cebf5db852
- https://github.com/peopledoc/vault-cli
- https://github.com/peopledoc/vault-cli/releases/tag/3.0.0
- https://github.com/pypa/advisory-database/tree/main/vulns/vault-cli/PYSEC-2021-853.yaml
- https://podalirius.net/en/publications/grehack-2021-optimizing-ssti-payloads-for-jinja2
