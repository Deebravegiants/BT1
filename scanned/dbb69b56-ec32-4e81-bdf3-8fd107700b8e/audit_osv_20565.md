# [M] CVE-2021-3521

## Summary
Severity: Medium
Advisory: CVE-2021-3521
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-08-22
Source: https://osv.dev/vulnerability/CVE-2021-3521
Type: osv

## Details
There is a flaw in RPM's signature functionality. OpenPGP subkeys are associated with a primary key via a "binding signature." RPM does not check the binding signature of subkeys prior to importing them. If an attacker is able to add or socially engineer another party to add a malicious subkey to a legitimate public key, RPM could wrongly trust a malicious signature. The greatest impact of this flaw is to data integrity. To exploit this flaw, an attacker must either compromise an RPM repository or convince an administrator to install an untrusted RPM or public key. It is strongly recommended to only use RPMs and public keys from trusted sources.

## References
- https://access.redhat.com/security/cve/CVE-2021-3521
- https://security.gentoo.org/glsa/202210-22
- https://bugzilla.redhat.com/show_bug.cgi?id=1941098
- https://github.com/rpm-software-management/rpm/commit/bd36c5dc9fb6d90c46fbfed8c2d67516fc571ec8
- https://github.com/rpm-software-management/rpm/pull/1795/
