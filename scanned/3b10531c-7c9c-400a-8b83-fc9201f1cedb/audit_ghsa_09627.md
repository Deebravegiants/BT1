# [M] OpenC3 COSMOS is Vulnerable to Self-XSS Through the Command Sender

## Summary
Severity: Medium
Advisory: GHSA-ffq5-qpvf-xq7x
CVE: CVE-2026-42086
CWE: CWE-79
Ecosystem: PyPI, RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-ffq5-qpvf-xq7x
Type: github-advisory

## Affected
- RubyGems: `openc3` — affected >=0 <7.0.0
- PyPI: `openc3` — affected >=0 <7.0.0

## Details
### Summary
The Command Sender UI uses an unsafe `eval()` function on array-like command parameters, which allows a user-supplied payload to execute in the browser when sending a command. This creates a self-XSS risk because an attacker can trigger their own script execution in the victim’s session, if allowed to influence the array parameter input, for example via phishing. If successful, an attacker may read or modify data in the authenticated browser context, including session tokens in local storage.

### Details
The unsafe `eval()`  usage on user-supplied ARRAY parameters happens in `convertToValue` method in [CommandSender.vue](https://github.com/OpenC3/cosmos/blob/main/openc3-cosmos-init/plugins/packages/openc3-cosmos-tool-cmdsender/src/tools/CommandSender/CommandSender.vue)

### PoC
1.	Using a drop-down form, choose any command that supports ARRAY parameters,
2.	Inside square brackets “[…]” place a JavaScript code to be executed
3.	Send command to CmdTlmServer using dedicated “Send” button 
4.	Observe JavaScript code being executed in the current browser session context

Below example uses `INST ARYCMD` to execute simple JavaScript code snippet `alert(“XSS”)`.
<img width="947" height="356" alt="image" src="https://github.com/user-attachments/assets/6fbdb6c9-616a-4268-bbb8-a8a1044437ad" />

<img width="942" height="545" alt="image" src="https://github.com/user-attachments/assets/4df24353-aea0-4aa0-adcf-b7c7e387dc83" />

### Impact
Local JavaScript execution in the user's browser

## References
- https://github.com/OpenC3/cosmos/security/advisories/GHSA-ffq5-qpvf-xq7x
- https://nvd.nist.gov/vuln/detail/CVE-2026-42086
- https://github.com/OpenC3/cosmos
- https://github.com/pypa/advisory-database/tree/main/vulns/openc3/PYSEC-2026-105.yaml
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/openc3/CVE-2026-42086.yml
