# [H] ZendFramework local file inclusion vector in `Zend_View::setScriptPath()` and `render()`

## Summary
Severity: High
Advisory: GHSA-hx3m-959f-v849
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-hx3m-959f-v849
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.7.0 <1.7.5

## Details
Zend_View is a component that utilizes PHP as a templating language. To utilize it, you specify "script paths" that contain view scripts, and then `render()` view scripts by specifying subdirectories within those script paths; the output is then returned as a string value which may be cached or directly output.

`Zend_View::setScriptPath()` in versions up to and including 1.7.4 include a potential Local File Inclusion vulnerability. If untrusted input is used to specify the script path and/or view script itself, a malicious attacker could potentially specify a system directory and thus render a system file.

As an example, if the user-supplied string `/etc/passwd` or a relative path that resolved to that file, was supplied to `Zend_View::render()`, that file would be rendered.

## References
- https://framework.zend.com/security/advisory/ZF2009-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2009-01.yaml
- https://github.com/zendframework/zf1
