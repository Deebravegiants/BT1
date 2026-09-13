# [H] CVE-2021-20230

## Summary
Severity: High
Advisory: CVE-2021-20230
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2021-20230
Type: osv

## Details
A flaw was found in stunnel before 5.57, where it improperly validates client certificates when it is configured to use both redirect and verifyChain options. This flaw allows an attacker with a certificate signed by a Certificate Authority, which is not the one accepted by the stunnel server, to access the tunneled service instead of being redirected to the address specified in the redirect option. The highest threat from this vulnerability is to confidentiality.

## References
- https://security.gentoo.org/glsa/202105-02
- https://bugzilla.redhat.com/show_bug.cgi?id=1925226
- https://github.com/mtrojnar/stunnel/commit/ebad9ddc4efb2635f37174c9d800d06206f1edf9
