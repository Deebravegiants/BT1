# [C] Google::Auth versions before 0.06 for Perl run a command named in an external_account credentials JSON via an ungated system call

## Summary
Severity: Critical
Advisory: CVE-2026-66902
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-04
Source: https://osv.dev/vulnerability/CVE-2026-66902
Type: osv

## Details
Google::Auth versions before 0.06 for Perl run a command named in an external_account credentials JSON via an ungated system call.

The Pluggable subclass reads credential_source.executable.command from the credentials JSON and runs it as `system($command)`, a single argument call that passes the whole string to /bin/sh -c. The executable's environment_variables map from the same JSON is copied into %ENV first. No opt-in gate guards the call. make_creds selects the Pluggable subclass whenever credential_source.executable is present, so the path is reached from the standard Application Default Credentials flow, including a "type": "external_account" configuration read from the file named by GOOGLE_APPLICATION_CREDENTIALS. Configurations without credential_source.executable do not select this subclass and do not reach the call.

Any caller that builds credentials from a configuration it does not fully control runs the embedded command with the privileges of the application process.

## References
- http://www.openwall.com/lists/oss-security/2026/08/04/35
- https://cpan.org/modules
- https://metacpan.org/release/CJCOLLIER/Google-Auth-0.06/diff/CJCOLLIER/Google-Auth-0.05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/66xxx/CVE-2026-66902.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-66902
- https://github.com/GoogleCloudPlatform/google-auth-library-perl/commit/c95c77e70bec94f17e239d88050f843ea1cade95.patch
- https://github.com/GoogleCloudPlatform/google-auth-library-perl
