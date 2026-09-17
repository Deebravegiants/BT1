# [M] CVE-2021-47016

## Summary
Severity: Medium
Advisory: CVE-2021-47016
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2021-47016
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

m68k: mvme147,mvme16x: Don't wipe PCC timer config bits

Don't clear the timer 1 configuration bits when clearing the interrupt flag
and counter overflow. As Michael reported, "This results in no timer
interrupts being delivered after the first. Initialization then hangs
in calibrate_delay as the jiffies counter is not updated."

On mvme16x, enable the timer after requesting the irq, consistent with
mvme147.

## References
- https://git.kernel.org/stable/c/43262178c043032e7c42d00de44c818ba05f9967
- https://git.kernel.org/stable/c/5d34225169346cab5145978d153b9ce90e9ace21
- https://git.kernel.org/stable/c/73fdeb612d25b5e105c219e05434285a45d23576
- https://git.kernel.org/stable/c/f6a90818a32058fca62cda3a2027a6a2364e1878
- https://git.kernel.org/stable/c/1dfb26df15fc7036a74221d43de7427f74293dae
