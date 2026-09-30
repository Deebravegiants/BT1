# [M] CVE-2019-16768

## Summary
Severity: Medium
Advisory: CVE-2019-16768
Aliases: GHSA-3r8j-pmch-5j2h
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-12-05
Source: https://osv.dev/vulnerability/CVE-2019-16768
Type: osv

## Details
In affected versions of Sylius, exception messages from internal exceptions (like database exception) are wrapped by \Symfony\Component\Security\Core\Exception\AuthenticationServiceException and propagated through the system to UI. Therefore, some internal system information may leak and be visible to the customer. A validation message with the exception details will be presented to the user when one will try to log into the shop. This has been patched in versions 1.3.14, 1.4.10, 1.5.7, and 1.6.3.

## References
- https://github.com/Sylius/Sylius/commit/be245302dfc594d8690fe50dd47631d186aa945f
- https://github.com/Sylius/Sylius/security/advisories/GHSA-3r8j-pmch-5j2h
