# [H] Metasploit Framework user exposes Metasploit to same deserialization issue that is exploited by that module

## Summary
Severity: High
Advisory: GHSA-xgww-h98f-24qf
CVE: CVE-2020-7385
CWE: CWE-502
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-xgww-h98f-24qf
Type: github-advisory

## Affected
- RubyGems: `metasploit-framework` — affected >=0 <4.19.0

## Details
By launching the drb_remote_codeexec exploit, a Metasploit Framework user will inadvertently expose Metasploit to the same deserialization issue that is exploited by that module, due to the reliance on the vulnerable Distributed Ruby class functions. Since Metasploit Framework typically runs with elevated privileges, this can lead to a system compromise on the Metasploit workstation. Note that an attacker would have to lie in wait and entice the Metasploit user to run the affected module against a malicious endpoint in a "hack-back" type of attack. Metasploit is only vulnerable when the drb_remote_codeexec module is running. In most cases, this cannot happen automatically.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7385
- https://github.com/rapid7/metasploit-framework/pull/14300
- https://github.com/rapid7/metasploit-framework/pull/14335
- https://github.com/rapid7/metasploit-framework
- https://help.rapid7.com/metasploit/release-notes/archive/2020/10
