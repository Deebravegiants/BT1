# [C] CVE-2019-9792

## Summary
Severity: Critical
Advisory: CVE-2019-9792
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-04-26
Source: https://osv.dev/vulnerability/CVE-2019-9792
Type: osv

## Details
The IonMonkey just-in-time (JIT) compiler can leak an internal JS_OPTIMIZED_OUT magic value to the running script during a bailout. This magic value can then be used by JavaScript to achieve memory corruption, which results in a potentially exploitable crash. This vulnerability affects Thunderbird < 60.6, Firefox ESR < 60.6, and Firefox < 66.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-07/
- https://www.mozilla.org/security/advisories/mfsa2019-08/
- https://www.mozilla.org/security/advisories/mfsa2019-11/
- https://access.redhat.com/errata/RHSA-2019:0966
- https://access.redhat.com/errata/RHSA-2019:1144
- https://bugzilla.mozilla.org/show_bug.cgi?id=1532599
- http://packetstormsecurity.com/files/153106/Spidermonkey-IonMonkey-JS_OPTIMIZED_OUT-Value-Leak.html
