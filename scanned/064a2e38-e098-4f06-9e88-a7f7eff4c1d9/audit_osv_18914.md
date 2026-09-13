# [M] CVE-2020-4042

## Summary
Severity: Medium
Advisory: CVE-2020-4042
Aliases: GHSA-vqpj-2vhj-h752
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2020-07-10
Source: https://osv.dev/vulnerability/CVE-2020-4042
Type: osv

## Details
Bareos before version 19.2.8 and earlier allows a malicious client to communicate with the director without knowledge of the shared secret if the director allows client initiated connection and connects to the client itself. The malicious client can replay the Bareos director's cram-md5 challenge to the director itself leading to the director responding to the replayed challenge. The response obtained is then a valid reply to the directors original challenge. This is fixed in version 19.2.8.

## References
- https://bugs.bareos.org/view.php?id=1250
- https://github.com/bareos/bareos/security/advisories/GHSA-vqpj-2vhj-h752
