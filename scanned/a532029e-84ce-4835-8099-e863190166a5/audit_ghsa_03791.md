# [C] Improper Verification of Cryptographic Signature in django-rest-registration

## Summary
Severity: Critical
Advisory: GHSA-p3w6-jcg4-52xh
CVE: CVE-2019-13177
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-07-02
Source: https://github.com/advisories/GHSA-p3w6-jcg4-52xh
Type: github-advisory

## Affected
- PyPI: `django-rest-registration` — affected >=0.2.0 <0.5.0

## Details
## Misusing the Django Signer API leads to predictable signatures used in verification emails

### Impact
The vulnerability is a high severity one. Anyone using Django REST Registration library versions `0.2.*` - `0.4.*` with e-mail verification option (which is recommended, but needs [additional configuration](https://django-rest-registration.readthedocs.io/en/latest/quickstart.html#preferred-configuration)) is affected.
In the worst case, the attacker can take over any Django user by resetting his/her password without even receiving the reset password verification link, just by guessing the signature from publicly available data (more detailed description below).

### Patches
The problem has been patched in version `0.5.0`. All library users should upgrade to version `0.5.0` or higher.
The fix will invalidate all previously generated signatures , and in consequence, all verification links in previously sent verification e-mails. Therefore semi-major version `0.5.0` was released instead of version `0.4.6` to mark that incompatibility.

### Workarounds
The easiest way way is to disable the verification options by using something like the minimal configuration described [here](https://django-rest-registration.readthedocs.io/en/latest/quickstart.html#minimal-configuration). This will unfortunately disable checking whether the given e-mail is valid and make unable to users who registered an account but didn't verify it before config change.

Less harsh way is to temporarily disable just the the reset password functionality:

```python
REST_REGISTRATION = {
    # ...
    'RESET_PASSWORD_VERIFICATION_ENABLED': False,
    # ...
}
```
Which should disallow the worst case, which is account takeover by an attacker. The attacker can still use the register-email endpoint to change the email to its own (but it is less critical than resetting the password in this case).

If one already set `'RESET_PASSWORD_VERIFICATION_ONE_TIME_USE'` setting key to `True` in `REST_REGISTRATION` Django setting (which is not the default setting) then it should mitigate the security issue in case of password reset (in this case, the signature is much harder to guess by the attacker). But even in this case upgrade to newest version is highly recommended.

### Technical description
After the code [was refactored](https://github.com/apragacz/django-rest-registration/commit/b6d921e9decc9bb36a4c6d58bc607471aa824a2e) to use the [official Signer class](https://docs.djangoproject.com/en/dev/topics/signing/) the salt
was passed wrongly as secret key, replacing the `SECRET_KEY` set in
Django settings file. This leads to the Django `SECRET_KEY` not being used by the signer object. The secret key of the signer ends to be the salt which in most cases is a static string which is publicly available.

In consequence this allows, with verification enabled, to guess
the signature contained in the verification link (which is sent in a verification e-mail) by a potential attacker very easily.

The bug went unnoticed for very long time so multiple versions are affected:
this bug affects versions `0.2.*`, `0.3.*`, `0.4.*`; version `0.1.*` is not affected.

Recently released version `0.5.0` contains the [fix](https://github.com/apragacz/django-rest-registration/commit/26d094fab65ea8c2694fdfb6a3ab95a7808b62d5) which correctly passes the salt to the Signer constructor as keyword argument instead as a positonal argument. It also contains additonal test so this problem should not reappear in the future.

### Thanks
I'd like to thank @peterthomassen from https://desec.io DNS security project for finding the bug. I'd like also to thank his employer, SSE (https://www.securesystems.de) for funding his work.


### For more information
If you have any questions or comments about this advisory:
* Open an issue in [GitHub issues project page](https://github.com/apragacz/django-rest-registration/issues)
* Email @apragacz, author of the library

## References
- https://github.com/apragacz/django-rest-registration/security/advisories/GHSA-p3w6-jcg4-52xh
- https://nvd.nist.gov/vuln/detail/CVE-2019-13177
- https://github.com/apragacz/django-rest-registration/commit/26d094fab65ea8c2694fdfb6a3ab95a7808b62d5
- https://github.com/advisories/GHSA-p3w6-jcg4-52xh
- https://github.com/apragacz/django-rest-registration
- https://github.com/apragacz/django-rest-registration/releases/tag/0.5.0
- https://github.com/pypa/advisory-database/tree/main/vulns/django-rest-registration/PYSEC-2019-20.yaml
