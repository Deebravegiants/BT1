# [H] Out-of-bounds write in nix::unistd::getgrouplist

## Summary
Severity: High
Advisory: GHSA-wgrg-5h56-jg27
Ecosystem: crates.io
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-wgrg-5h56-jg27
Type: github-advisory

## Affected
- crates.io: `nix` — affected >=0.16.0 <0.20.2
- crates.io: `nix` — affected >=0.21.0 <0.21.2
- crates.io: `nix` — affected >=0.22.0 <0.22.2

## Details
On certain platforms, if a user has more than 16 groups, the
`nix::unistd::getgrouplist` function will call the libc `getgrouplist`
function with a length parameter greater than the size of the buffer it
provides, resulting in an out-of-bounds write and memory corruption.

The libc `getgrouplist` function takes an in/out parameter `ngroups`
specifying the size of the group buffer. When the buffer is too small to
hold all of the reqested user's group memberships, some libc
implementations, including glibc and Solaris libc, will modify `ngroups`
to indicate the actual number of groups for the user, in addition to
returning an error. The version of `nix::unistd::getgrouplist` in nix
0.16.0 and up will resize the buffer to twice its size, but will not
read or modify the `ngroups` variable. Thus, if the user has more than
twice as many groups as the initial buffer size of 8, the next call to
`getgrouplist` will then write past the end of the buffer.

The issue would require editing /etc/groups to exploit, which is usually
only editable by the root user.

## References
- https://github.com/nix-rust/nix/issues/1541
- https://github.com/nix-rust/nix
- https://rustsec.org/advisories/RUSTSEC-2021-0119.html
