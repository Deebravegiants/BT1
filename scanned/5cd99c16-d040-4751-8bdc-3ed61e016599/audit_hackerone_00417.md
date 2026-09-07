# [M] Unpacker improperly validates symlinks, allowing gems writes to arbitrary locations

## Summary
Severity: Medium
Program: RubyGems
Weakness: Path Traversal
Reporter: nmalkin
State: resolved
Disclosed: 2018-12-31T08:05:52.196Z
Source: https://hackerone.com/reports/270072

## Details
# Unpacker improperly validates symlinks, allowing gems writes to arbitrary locations

The RubyGems installer attempts to prevent a gem from writing any files outside the install directory; however it is possible to bypass the check with a symbolic link in a crafted gem.

## Example structure of malicious gem
```
$ tar -xvf symlink.gem
metadata.gz
data.tar.gz
$ tar -tvf data.tar.gz
-rw-r--r-- 0/0              12 1969-12-31 16:00 README
lrw-r--r-- 0/0               0 1969-12-31 16:00 link -> /tmp
-rw-r--r-- 0/0               6 1969-12-31 16:00 link/HACKED
```


## Proof of concept
Using the attached `symlink.gem`:
```
gem install symlink.gem
# or
gem unpack symlink.gem
```
This will create a file /tmp/HACKED.

## Impact

The name and contents of the written file, as well as the file permissions, are arbitrary.
Using this technique, an attacker could easily get code execution, for example by overwriting a system binary or writing into a user's `.profile`.

Note that the exploit will even work with `gem unpack`, which is supposed to be safe of system-level side-effects.

For comparison, this exploit is more powerful than #243156 (and #270068) as the target directory doesn't need to contain a dash.

## Root cause

The code in [install_location](https://github.com/rubygems/rubygems/blob/v2.6.13/lib/rubygems/package.rb#L415) is supposed to check if the target filename is outside the destination directory. It does this by fully resolving (using `File.realpath`) the destination directory and then seeing if the target filename `.start_with?` that directory.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/270072_
