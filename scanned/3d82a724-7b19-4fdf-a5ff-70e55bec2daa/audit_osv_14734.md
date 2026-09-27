# [H] CVE-2019-11189

## Summary
Severity: High
Advisory: CVE-2019-11189
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-02-20
Source: https://osv.dev/vulnerability/CVE-2019-11189
Type: osv

## Details
Authentication Bypass by Spoofing in org.onosproject.acl (access control) and org.onosproject.mobility (host mobility) in ONOS v2.0 and earlier allows attackers to bypass network access control via data plane packet injection. To exploit the vulnerability, an attacker sends a gratuitous ARP reply that causes the host mobility application to remove existing access control flow denial rules in the network. The access control application does not re-install flow deny rules, so the attacker can bypass the intended access control policy.

## References
- https://www.ndss-symposium.org/wp-content/uploads/2020/02/24080.pdf
