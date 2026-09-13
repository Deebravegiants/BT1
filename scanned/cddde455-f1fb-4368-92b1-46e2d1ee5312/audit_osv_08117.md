# [H] CVE-2016-10363

## Summary
Severity: High
Advisory: CVE-2016-10363
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-16
Source: https://osv.dev/vulnerability/CVE-2016-10363
Type: osv

## Details
Logstash versions prior to 2.3.3, when using the Netflow Codec plugin, a remote attacker crafting malicious Netflow v5, Netflow v9 or IPFIX packets could perform a denial of service attack on the Logstash instance. The errors resulting from these crafted inputs are not handled by the codec and can cause the Logstash process to exit.

## References
- https://www.elastic.co/community/security
