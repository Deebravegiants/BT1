# [H] Puma used with Rails may lead to Information Exposure

## Summary
Severity: High
Advisory: GHSA-rmj8-8hhh-gv5h
CVE: CVE-2022-23634
CWE: CWE-200, CWE-404
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-rmj8-8hhh-gv5h
Type: github-advisory

## Affected
- RubyGems: `puma` — affected >=5.0.0 <5.6.2
- RubyGems: `puma` — affected >=0 <4.3.11

## Details
### Impact
Prior to `puma` version `5.6.2`, `puma` may not always call `close` on the response body. Rails, prior to version `7.0.2.2`, depended on the response body being closed in order for its `CurrentAttributes` implementation to work correctly.

From Rails:

> Under certain circumstances response bodies will not be closed, for example a bug in a webserver[1] or a bug in a Rack middleware. In the event a response is not notified of a close, ActionDispatch::Executor will not know to reset thread local state for the next request. This can lead to data being leaked to subsequent requests, especially when interacting with ActiveSupport::CurrentAttributes.

The combination of these two behaviors (Puma not closing the body + Rails' Executor implementation) causes information leakage.

### Patches
This problem is fixed in Puma versions 5.6.2 and 4.3.11.

This problem is fixed in Rails versions 7.02.2, 6.1.4.6, 6.0.4.6, and 5.2.6.2.

See: 
https://github.com/advisories/GHSA-wh98-p28r-vrc9 
for details about the rails vulnerability

Upgrading to a patched Rails _or_ Puma version fixes the vulnerability.

### Workarounds

Upgrade to Rails versions 7.02.2, 6.1.4.6, 6.0.4.6, and 5.2.6.2.

The [Rails CVE](https://groups.google.com/g/ruby-security-ann/c/FkTM-_7zSNA/m/K2RiMJBlBAAJ?utm_medium=email&utm_source=footer&pli=1) includes a middleware that can be used instead.

### References

* Rails CVE: [CVE-2022-23633](https://groups.google.com/g/ruby-security-ann/c/FkTM-_7zSNA/m/K2RiMJBlBAAJ?utm_medium=email&utm_source=footer&pli=1)

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [puma](https://github.com/puma/puma)
* See our [security policy](https://github.com/puma/puma/security/policy)

## References
- https://github.com/puma/puma/security/advisories/GHSA-rmj8-8hhh-gv5h
- https://nvd.nist.gov/vuln/detail/CVE-2022-23634
- https://github.com/puma/puma/commit/b70f451fe8abc0cff192c065d549778452e155bb
- https://github.com/advisories/GHSA-rmj8-8hhh-gv5h
- https://github.com/advisories/GHSA-wh98-p28r-vrc9
- https://github.com/puma/puma
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/puma/CVE-2022-23634.yml
- https://groups.google.com/g/ruby-security-ann/c/FkTM-_7zSNA/m/K2RiMJBlBAAJ?utm_medium=email&utm_source=footer&pli=1
- https://lists.debian.org/debian-lts-announce/2022/05/msg00034.html
- https://lists.debian.org/debian-lts-announce/2022/08/msg00015.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/F6YWGIIKL7KKTS3ZOAYMYPC7D6WQ5OA5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/L7NESIBFCNSR3XH7LXDPKVMSUBNUB43G
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TUBFJ44NCKJ34LECZRAP4N5VL6USJSIB
- https://security.gentoo.org/glsa/202208-28
- https://www.debian.org/security/2022/dsa-5146
