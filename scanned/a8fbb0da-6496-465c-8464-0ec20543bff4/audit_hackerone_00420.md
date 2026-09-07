# [M] Installer can modify other gems if gem name is specially crafted

## Summary
Severity: Medium (CVSS 5.5)
Program: RubyGems
Weakness: Path Traversal
Reporter: nmalkin
State: resolved
Disclosed: 2018-03-22T04:54:02.816Z
Source: https://hackerone.com/reports/270068

## Details
# Installer can modify other gems if gem name is specially crafted

The `install_location` function allows writing to certain files outside the installation directory.

The `install_location` function in lib/rubygems/package.rb attempts to ensure that files are not installed outside `destination_dir`.  However the test it employs, a string comparison using `start_with?`, fails to prevent the case when `destination_dir` is a prefix of the path being written.

Example that should be prevented but is allowed:
```
install_location '../install-whatever-foobar/hello.txt', '/tmp/install'
# outputs '/tmp/install-whatever-foobar/hello.txt'
```

`gem install` always constructs `destination_dir` as `'#{name}-#{version}'`, so the vulnerability cannot overwrite arbitrary files.  However, a malicious gem with `name='rails'` and an empty version number (`version=''`), for example, could overwrite the files of any other gem whose name begins with `rails-`, like rails-i18n or rails-letsencrypt.

## Proof of concept

The attached ra.gem demonstrates the vulnerability. It assumes that some other gems have already been installed.

```bash
gem install --install-dir=/tmp/install rails-i18n rails-letsencrypt rails-html-sanitizer
gem install --install-dir=/tmp/install ra.gem
```

The malicious gem will do three things, each of which could potentially lead to code execution:

- delete an existing rails-letsencrypt-0.5.3 gem
- overwrite a code file in the rails-i18n-5.0.4 gem
- symlink rails-html-sanitizer-1.0.3 to a world-writable directory

The structure of the gem file reveals how the attack works:

```sh
$ tar -xvf ra.gem
metadata.gz
data.tar.gz
$ gzip -dc metadata.gz | head -n 4
--- !ruby/object:Gem::Specification
name: rails
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/270068_
