# [M] CVE-2018-1000815

## Summary
Severity: Medium
Advisory: CVE-2018-1000815
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-1000815
Type: osv

## Details
Brave Software Inc. Brave version version 0.22.810 to 0.24.0 contains a Other/Unknown vulnerability in function ContentSettingsObserver::AllowScript() in content_settings_observer.cc that can result in Websites can run inline JavaScript even if script is blocked, making attackers easier to track users. This attack appear to be exploitable via the victim must visit a specially crafted website. This vulnerability appears to have been fixed in 0.25.2.

## References
- https://github.com/brave/browser-laptop/issues/15232
- https://github.com/brave/muon/commit/c18663aa171c6cdf03da3e8c70df8663645b97c4
- https://github.com/brave/muon/pull/651
