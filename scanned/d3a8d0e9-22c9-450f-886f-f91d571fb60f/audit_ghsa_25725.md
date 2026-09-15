# [M] Improper Authorization in cobbler

## Summary
Severity: Medium
Advisory: GHSA-mcg6-h362-cmq5
CVE: CVE-2022-0860
CWE: CWE-285, CWE-863
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-03-11
Source: https://github.com/advisories/GHSA-mcg6-h362-cmq5
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.3.2

## Details
### Impact

If PAM is correctly configured and a user account is set to expired, the expired user-account is still able to successfully log into Cobbler in all places (Web UI, CLI & XMLRPC-API).

The same applies to user accounts with passwords set to be expired.

### Patches

There is a patch for the latest Cobbler `3.3.2` available, however a backport will be done for `3.2.x`.

### Workarounds

- Delete expired accounts which are able to access Cobbler via PAM.
- Use `chage -l <username>` to lock the account. If the account has SSH-Keys attached then remove them completely.

### References

- Originally discovered by @ysf at https://www.huntr.dev/bounties/c458b868-63df-414e-af10-47e3745caa1d/

### How to test if my Cobbler instance is affected?

The following `pytest` test assumes that your PAM setup is correct. In case the added user is not able to login, this test does not make sense to be executed.

```python
def test_pam_login_with_expired_user():
    # Arrange
    # create pam testuser
    test_username = "expired_user"
    test_password = "password"
    test_api = CobblerAPI()
    subprocess_1 = subprocess.run(
        ["perl", "-e", "'print crypt(\"%s\", \"%s\")'" % (test_username, test_password)],
        stdout=subprocess.PIPE
    )
    subprocess.run(["useradd", "-p", subprocess_1.stdout, test_username])
    # change user to be expired
    subprocess.run(["chage", "-E0", test_username])

    # Act
    result = pam.authenticate(test_api, test_username, test_password)

    # Assert - login should fail
    assert not result
```

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [the Cobbler repository](https://github.com/cobbler/cobbler/issues/new/choose)
* Ask in the [Gitter/Matrix Chat](https://gitter.im/cobbler/community)
* Email us at [cobbler.project@gmail.com](mailto:cobbler.project@gmail.com)

## References
- https://github.com/cobbler/cobbler/security/advisories/GHSA-mcg6-h362-cmq5
- https://nvd.nist.gov/vuln/detail/CVE-2022-0860
- https://github.com/cobbler/cobbler/commit/9044aa990a94752fa5bd5a24051adde099280bfa
- https://github.com/advisories/GHSA-mcg6-h362-cmq5
- https://github.com/cobbler/cobbler
- https://github.com/pypa/advisory-database/tree/main/vulns/cobbler/PYSEC-2022-177.yaml
- https://huntr.dev/bounties/c458b868-63df-414e-af10-47e3745caa1d
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/D4KCNZYBQC2FM5SEEDRQZO4LRZ4ZECMG
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DYWYHWVVRUSPCV5SWBOSAMQJQLTSBTKY
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/IYSHMF6MEIITFAG7EJ3IQKVUN7MDV2XM
