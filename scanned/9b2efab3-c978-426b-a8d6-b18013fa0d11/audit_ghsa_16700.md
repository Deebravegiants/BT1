# [H] Grav Vulnerable to Arbitrary File Read to Account Takeover

## Summary
Severity: High
Advisory: GHSA-f8v5-jmfh-pr69
CVE: CVE-2024-34082
CWE: CWE-22, CWE-269
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:L (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-f8v5-jmfh-pr69
Type: github-advisory

## Affected
- Packagist: `getgrav/grav` — affected >=0 <1.7.46

## Details
### Summary
A low privilege user account with page edit privilege can read any server files using Twig Syntax. This includes Grav user account files - /grav/user/accounts/*.yaml. This file stores hashed user password, 2FA secret, and the password reset token. This can allow an adversary to compromise any registered account by resetting a password for a user to get access to the password reset token from the file or by cracking the hashed password.

### Proof Of Concept
`{{ read_file('/var/www/html/grav/user/accounts/riri.yaml') }}`

Use the above Twig template syntax in a page and observe that the administrator riri's authentication details are exposed accessible by any unauthenticated user. 

![file-read-2-ATO](https://github.com/getgrav/grav/assets/48800246/9dee4daa-f029-40dd-9646-94c794d3f254)

As an additional proof of concept for reading system files, observe the `/etc/passwd` file read using the following Twig syntax:
`{{ read_file('/etc/passwd') }}`

![file-read-etc-passwd](https://github.com/getgrav/grav/assets/48800246/e45de4d4-f81f-42cf-8466-aa36b225ca94)

### Impact
This can allow a low privileged user to perform a full account takeover of other registered users including Adminsitrators. This can also allow an adversary to read any file in the web server.

## References
- https://github.com/getgrav/grav/security/advisories/GHSA-f8v5-jmfh-pr69
- https://nvd.nist.gov/vuln/detail/CVE-2024-34082
- https://github.com/getgrav/grav/commit/b6bba9eb99bf8cb55b8fa8d23f18873ca594e348
- https://github.com/getgrav/grav
