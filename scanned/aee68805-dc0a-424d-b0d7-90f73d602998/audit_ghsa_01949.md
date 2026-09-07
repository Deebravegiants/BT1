# [M] Form validation can be skipped

## Summary
Severity: Medium
Advisory: GHSA-m5vx-8chx-qvmm
CVE: CVE-2021-32697
CWE: CWE-20
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-m5vx-8chx-qvmm
Type: github-advisory

## Affected
- Packagist: `neos/form` — affected >=1.2.0 <4.3.3
- Packagist: `neos/form` — affected >=5.0.0 <5.0.9
- Packagist: `neos/form` — affected >=5.1.0 <5.1.3

## Details
### Impact
By crafting a special `GET` request containing a valid form state, a form can be submitted without invoking any validators.
We consider the severity _low_ because it is not possible to _change_ any form values since the form state is secured with an HMAC that is still verified.
That means that this issue can only be exploited if Form Finishers cause side effects even if no form values have been sent.

### Patches
https://github.com/neos/form/commit/69de4219b1f58157e2be6b05811463875d75c246

### Workarounds
Form Finishers can be adjusted in a way that they only execute an action if the submitted form contains some expected data.
Alternatively a custom Finisher can be added as first finisher.

### References
This regression was introduced with https://github.com/neos/form/commit/049d415295be8d4a0478ccba97dba1bb81649567
Original report: https://tickets.neos.io/#ticket/zoom/411 (internal)

## References
- https://github.com/neos/form/security/advisories/GHSA-m5vx-8chx-qvmm
- https://nvd.nist.gov/vuln/detail/CVE-2021-32697
- https://github.com/neos/form-ghsa-m5vx-8chx-qvmm/pull/1
- https://github.com/neos/form/commit/049d415295be8d4a0478ccba97dba1bb81649567
- https://github.com/neos/form/commit/69de4219b1f58157e2be6b05811463875d75c246
- https://github.com/FriendsOfPHP/security-advisories/blob/master/neos/form/CVE-2021-32697.yaml
- https://github.com/neos/form/releases/tag/5.1.3
