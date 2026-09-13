# [H] CVE-2020-35766

## Summary
Severity: High
Advisory: CVE-2020-35766
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-28
Source: https://osv.dev/vulnerability/CVE-2020-35766
Type: osv

## Details
The test suite in libopendkim in OpenDKIM through 2.10.3 allows local users to gain privileges via a symlink attack against the /tmp/testkeys file (related to t-testdata.h, t-setup.c, and t-cleanup.c). NOTE: this is applicable to persons who choose to engage in the "A number of self-test programs are included here for unit-testing the library" situation.

## References
- https://github.com/trusteddomainproject/OpenDKIM/issues/113
