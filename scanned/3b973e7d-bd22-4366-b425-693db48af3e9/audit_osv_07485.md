# [C] Apache Solr information disclosure vulnerability through DataImportHandler

## Summary
Severity: Critical
Advisory: BIT-solr-2021-44548
Aliases: CVE-2021-44548, GHSA-pccr-q7v9-5f27
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-solr-2021-44548
Type: osv

## Affected
- Bitnami: `solr` — affected >=0 <8.11.1

## Details
An Improper Input Validation vulnerability in DataImportHandler of Apache Solr allows an attacker to provide a Windows UNC path resulting in an SMB network call being made from the Solr host to another host on the network. If the attacker has wider access to the network, this may lead to SMB attacks, which may result in: * The exfiltration of sensitive data such as OS user hashes (NTLM/LM hashes), * In case of misconfigured systems, SMB Relay Attacks which can lead to user impersonation on SMB Shares or, in a worse-case scenario, Remote Code Execution This issue affects all Apache Solr versions prior to 8.11.1. This issue only affects Windows.

## References
- https://security.netapp.com/advisory/ntap-20220114-0005/
- https://solr.apache.org/security.html#cve-2021-44548-apache-solr-information-disclosure-vulnerability-through-dataimporthandler
- https://nvd.nist.gov/vuln/detail/CVE-2021-44548
