# [C] s390/ism: fix concurrency management in ism_cmd()

## Summary
Severity: Critical
Advisory: CVE-2025-39726
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39726
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <6.6.101, >=6.7.0 <6.12.41, >=6.13.0 <6.15.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/ism: fix concurrency management in ism_cmd()

The s390x ISM device data sheet clearly states that only one
request-response sequence is allowable per ISM function at any point in
time.  Unfortunately as of today the s390/ism driver in Linux does not
honor that requirement. This patch aims to rectify that.

This problem was discovered based on Aliaksei's bug report which states
that for certain workloads the ISM functions end up entering error state
(with PEC 2 as seen from the logs) after a while and as a consequence
connections handled by the respective function break, and for future
connection requests the ISM device is not considered -- given it is in a
dysfunctional state. During further debugging PEC 3A was observed as
well.

A kernel message like
[ 1211.244319] zpci: 061a:00:00.0: Event 0x2 reports an error for PCI function 0x61a
is a reliable indicator of the stated function entering error state
with PEC 2. Let me also point out that a kernel message like
[ 1211.244325] zpci: 061a:00:00.0: The ism driver bound to the device does not support error recovery
is a reliable indicator that the ISM function won't be auto-recovered
because the ISM driver currently lacks support for it.

On a technical level, without this synchronization, commands (inputs to
the FW) may be partially or fully overwritten (corrupted) by another CPU
trying to issue commands on the same function. There is hard evidence that
this can lead to DMB token values being used as DMB IOVAs, leading to
PEC 2 PCI events indicating invalid DMA. But this is only one of the
failure modes imaginable. In theory even completely losing one command
and executing another one twice and then trying to interpret the outputs
as if the command we intended to execute was actually executed and not
the other one is also possible.  Frankly, I don't feel confident about
providing an exhaustive list of possible consequences.

## References
- https://git.kernel.org/stable/c/1194ad0d44d66b273a02a3a22882dc863a68d764
- https://git.kernel.org/stable/c/897e8601b9cff1d054cdd53047f568b0e1995726
- https://git.kernel.org/stable/c/faf44487dfc80817f178dc8de7a0b73f960d019b
- https://git.kernel.org/stable/c/fafaa4982bedb5532f5952000f714a3e63023f40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39726.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39726
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
