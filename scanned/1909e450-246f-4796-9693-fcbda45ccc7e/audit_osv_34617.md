# [C] Landlord Onboarding & Rental Signup Unauthorized Access Vulnerability in TurboTenant Stripe Integration

## Summary
Severity: Critical
Advisory: CVE-2025-62516
Aliases: GHSA-43cm-q3mv-2hvj
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-27
Source: https://osv.dev/vulnerability/CVE-2025-62516
Type: osv

## Details
Landlord Onboarding & Rental Signup introduces the landlord onboarding workflow and rental signup system for VivaTurbo Rentals & Property Services. In 2.0.0 and earlier, a vulnerability was identified in the TurboTenant property listing activation workflow that could allow unauthorized access to certain Stripe payment session data. This could potentially expose sensitive business metadata, including landlord dashboard sync details and tenant information. The issue affects the API endpoints handling the property listing activation, subscription metadata, and payment link generation.

## References
- https://github.com/turbo-tenant-internal-property/www.turbotenant.com/security/advisories/GHSA-43cm-q3mv-2hvj
