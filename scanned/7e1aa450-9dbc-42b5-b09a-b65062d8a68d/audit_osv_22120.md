# [M] /etc/pki/tls and /etc/ssl/certs include distrusted certificates in make-ca

## Summary
Severity: Medium
Advisory: CVE-2022-21672
Aliases: GHSA-m5qh-728v-4xrx
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2022-01-10
Source: https://osv.dev/vulnerability/CVE-2022-21672
Type: osv

## Details
make-ca is a utility to deliver and manage a complete PKI configuration for workstations and servers. Starting with version 0.9 and prior to version 1.10, make-ca misinterprets Mozilla certdata.txt and treats explicitly untrusted certificates like trusted ones, causing those explicitly untrusted certificates trusted by the system. The explicitly untrusted certificates were used by some CAs already hacked. Hostile attackers may perform a MIM attack exploiting them. Everyone using the affected versions of make-ca should upgrade to make-ca-1.10, and run `make-ca -f -g` as the `root` user to regenerate the trusted store immediately. As a workaround, users may delete the untrusted certificates from /etc/pki/tls and /etc/ssl/certs manually (or by a script), but this is not recommended because the manual changes will be overwritten next time running make-ca to update the trusted anchor.

## References
- https://lists.linuxfromscratch.org/sympa/arc/blfs-support/2022-01/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/21xxx/CVE-2022-21672.json
- https://github.com/lfs-book/make-ca/security/advisories/GHSA-m5qh-728v-4xrx
- https://nvd.nist.gov/vuln/detail/CVE-2022-21672
- https://github.com/lfs-book/make-ca/issues/19
- https://github.com/lfs-book/make-ca/pull/20
