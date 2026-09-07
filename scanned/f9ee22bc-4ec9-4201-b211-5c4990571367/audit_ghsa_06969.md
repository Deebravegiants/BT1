# [C] Active Storage has possible arbitrary file read and remote code execution in Active Storage variant processing

## Summary
Severity: Critical
Advisory: GHSA-xr9x-r78c-5hrm
CVE: CVE-2026-66066
CWE: CWE-1188
Ecosystem: RubyGems
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-07-30
Source: https://github.com/advisories/GHSA-xr9x-r78c-5hrm
Type: github-advisory

## Affected
- RubyGems: `activestorage` — affected >=0 <7.2.3.2
- RubyGems: `activestorage` — affected >=8.0.0.beta1 <8.0.5.1
- RubyGems: `activestorage` — affected >=8.1.0.beta1 <8.1.3.1

## Details
### Impact
In its default configuration, a Rails application that displays image variants may allow an
unauthenticated attacker to read arbitrary files from the server, including the process environment.
That environment typically holds `secret_key_base` and often credentials for external systems, which
may in turn allow escalation to remote code execution or lateral movement to those systems.

### Details
libvips reads and writes file formats through "loaders" and "savers" (or more generally
"operations"), many of which are backed by third-party libraries. It marks some of these operations
as "unfuzzed", meaning they are unsafe for untrusted content, and several handle formats unrelated
to web images. Active Storage did not disable the unfuzzed operations, so an attacker who can upload
a crafted file and cause a variant to be generated from it may be able to invoke one.

We are aware of a mechanism by which an attacker, by uploading a crafted file, is able to cause
disclosure of the contents of arbitrary files accessible on the filesystem of the targeted
application. One specific attack chain has been reported to us (see "Disclosure" below), but we do
not assume it is the only one that exists.

### Affected applications
An application is affected if it meets all of these requirements:
- Uses libvips for Active Storage image processing. This is `config.active_storage.variant_processor = :vips`,
  which `load_defaults 7.0` set and no later default has changed.
- Allows image uploads from untrusted users.

Generating variants is not a separate requirement.

### Mitigation
- Upgrade to a fixed version of `activestorage`.
- The minimum version of libvips must be upgraded to `>= 8.13`.
- Change `secret_key_base` and change any secrets accessible in the application environment (see "Expire and change secrets" below)

Earlier versions of libvips (`< 8.13`) cannot disable unfuzzed operations at all, and Active Storage
will raise an exception during boot in such an unsecurable environment.

### Expire and change secrets

Upgrading closes the vulnerability but does not undo an exfiltrated secret if that already
occurred. An affected application should treat every secret readable by the application process as
potentially exposed and change it, including:

- `secret_key_base`
- The master key, whether stored in `config/master.key` or supplied as `RAILS_MASTER_KEY`, along
  with everything in `config/credentials.yml.enc` that it decrypts
- Credentials for the Active Storage service, such as S3, GCS, or Azure keys
- Database credentials
- Tokens and keys for any third-party service the application calls

Changing `secret_key_base` expires active sessions and requires users to log in again. Encrypted
cookies, signed cookies, signed global IDs, and Active Storage URLs are also affected.

Rotation should only be used as an intermediate step if necessary. Do not retain an exposed secret
as a fallback.

### Workarounds
If libvips `< 8.13` is being used, there are no workarounds available other than removing the
dependency on libvips from the application. Some applications may have `ruby-vips` declared as a
dependency only for image analysis, and those applications may be able to simply remove `ruby-vips`
from the Gemfile to remove libvips from the application. Applications that do not use Active Storage
can remove `ruby-vips` from the Gemfile to avoid the boot-time checks.

If libvips `>= 8.13` is present on the system, applications can disable the unfuzzed operations
without upgrading Rails by setting the `VIPS_BLOCK_UNTRUSTED` environment variable, which libvips
reads while initializing.

Applications also running ruby-vips `>= 2.2.1` or later can instead call
`Vips.block_untrusted(true)` from an initializer.

### Releases
The fixed releases are available at the normal locations.

### Versions affected

- activestorage < 7.2.3.2
- activestorage >= 8.0, < 8.0.5.1
- activestorage >= 8.1, < 8.1.3.1

### Disclosure
Technical details of the attack chain are intentionally omitted from this advisory. They would add
nothing to an administrator's decision to upgrade, while making it substantially easier to attack
applications that have not yet done so.

Details will be disclosed no later than 2026-08-28, via the [Rails Security
Announcements](https://discuss.rubyonrails.org/c/security-announcements/9) forum.

### Credit
This issue was responsibly reported by [0xacb](https://x.com/0xacb), [s3np41k1r1t0](https://x.com/s3np41k1r1t0) and [castilho](https://x.com/castilho101) from [Ethiack](https://ethiack.com), and [RyotaK](https://ryotak.net) from [GMO Flatt Security Inc.](https://flatt.tech/en/).

### References
- libvips 8.13 release notes, [blocking of unfuzzed loaders](https://www.libvips.org/2022/05/28/What's-new-in-8.13.html#blocking-of-unfuzzed-loaders)
- W.A. Arbaugh, W.L. Fithen, and J. McHugh, ["Windows of Vulnerability: A Case Study
  Analysis"](https://doi.org/10.1109/2.889093), IEEE Computer 33(12), December 2000
- https://ethiack.com/info-hub/research/kindarails2shell-rails-rce-cve
- https://blog.flatt.tech/entry/kindarails2shell_rails

## References
- https://github.com/rails/rails/security/advisories/GHSA-xr9x-r78c-5hrm
- https://github.com/rails/rails/commit/1c01bb587206ee6eb0e1179c2cef96a6a47acb1e
- https://github.com/rails/rails/commit/349e7a5d5b4b715af1e416db824f3c078a7d59e5
- https://github.com/rails/rails/commit/d79b7f4aa17dec8ce4960fef05733c8c0c7ef49a
- https://github.com/rails/rails
- https://github.com/rails/rails/releases/tag/v7.2.3.2
- https://github.com/rails/rails/releases/tag/v8.0.5.1
- https://github.com/rails/rails/releases/tag/v8.1.3.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/activestorage/CVE-2026-66066.yml
- https://thehackernews.com/2026/07/critical-rails-flaw-could-let.html
- https://www.cve.org/CVERecord/SearchResults?query=CVE-2026-66066
