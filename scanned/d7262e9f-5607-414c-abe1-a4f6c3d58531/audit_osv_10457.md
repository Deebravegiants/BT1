# [H] CVE-2017-15865

## Summary
Severity: High
Advisory: CVE-2017-15865
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-11-08
Source: https://osv.dev/vulnerability/CVE-2017-15865
Type: osv

## Details
bgpd in FRRouting (FRR) before 2.0.2 and 3.x before 3.0.2, as used in Cumulus Linux before 3.4.3 and other products, allows remote attackers to obtain sensitive information via a malformed BGP UPDATE packet from a connected peer, which triggers transmission of up to a few thousand unintended bytes because of a mishandled attribute length, aka RN-690 (CM-18492).

## References
- http://www.securityfocus.com/bid/101794
- https://frrouting.org/community/security.html
- https://lists.cumulusnetworks.com/pipermail/cumulus-security-announce/2017-November/000009.html
- https://support.cumulusnetworks.com/hc/en-us/articles/115014754307#rn690
- https://support.cumulusnetworks.com/hc/en-us/articles/115014778107-CVE-2017-15865-Malformed-BGP-UPDATE-Triggers-Information-Disclosure
