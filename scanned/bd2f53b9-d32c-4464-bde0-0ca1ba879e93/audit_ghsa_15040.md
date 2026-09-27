# [H] Host header injection in the password reset

## Summary
Severity: High
Advisory: GHSA-mrqg-mwh7-q94j
CVE: CVE-2024-23648
CWE: CWE-74
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-01-24
Source: https://github.com/advisories/GHSA-mrqg-mwh7-q94j
Type: github-advisory

## Affected
- Packagist: `pimcore/admin-ui-classic-bundle` — affected >=0 <1.2.3

## Details
### Summary

The password reset functionality sends to the the user requesting a password change an email containing an URL to reset its password.

The URL sent contains a unique token, valid during 24 hours, allowing the user to reset its password.
This token is highly sensitive ; as an attacker able to retrieve it would be able to resets the user's password.

It was identified during the audit that the reset-password URL is crafted using the "Host" HTTP header of the request sent to request a password reset.

This way, an external attacker could send password requests for users, but specify a "Host" header of a website that they control.
If the user receiving the mail clicks on the link, the attacker would retrieve the reset token of the victim and perform account takeover.

### Details

This attack required the server to serve Pimcore on arbitrary "Host". This configuration would be plausible if the attacker is already behind the reverse proxy.
During the assessment of my client, their instance was accepting any Host header, and they did not received security recommendations that they should restrict this while installing Pimcore.

From what I understood of Pimcore, the vulnerability is in the "admin-ui-classic-bundle", in the file src/Controller/Admin/UserController.php.

The following screenshots provide evidences of the vulnerability. The environment of the test is : dockerized Pimcore v11.1.1 on default configuration (https://pimcore.com/docs/platform/Pimcore/Getting_Started/Installation/Docker_Based_Installation/).

### PoC
![image](https://user-images.githubusercontent.com/1197252/286258644-a3ad6993-babc-4673-bed3-ffeefe2e7f92.png)
![image](https://user-images.githubusercontent.com/1197252/286258657-bc0075b9-e62c-4f29-bb5f-95227b3f53c0.png)

### Remediation
Create a variable that sets the server host.
Don't enable password reset functionality while this variable is not set ; or make sure that the administrator knows what they are doing.

I believe that just documenting that the server should not serve on any Host would not be enough to enforce a remediation to this vulnerability.

The Snipe-IT project managed this same issue by creating a "APP_ALLOW_INSECURE_HOSTS" variable, and retrieving the app absolute URL from a config file :[ https://github.com/snipe/snipe-it/commit/0c4768fd2a11ac26a61814cef23a71061bfd8bcc](https://github.com/snipe/snipe-it/commit/0c4768fd2a11ac26a61814cef23a71061bfd8bcc)

### Impact
Could lead to a 1-click account takeover

## References
- https://github.com/pimcore/admin-ui-classic-bundle/security/advisories/GHSA-mrqg-mwh7-q94j
- https://nvd.nist.gov/vuln/detail/CVE-2024-23648
- https://github.com/pimcore/admin-ui-classic-bundle/commit/70f2205b5a5ea9584721d4f3e803f4d0dd5e4655
- https://github.com/pimcore/admin-ui-classic-bundle
