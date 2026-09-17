# [M] CVE-2021-47161

## Summary
Severity: Medium
Advisory: CVE-2021-47161
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-25
Source: https://osv.dev/vulnerability/CVE-2021-47161
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

spi: spi-fsl-dspi: Fix a resource leak in an error handling path

'dspi_request_dma()' should be undone by a 'dspi_release_dma()' call in the
error handling path of the probe function, as already done in the remove
function

## References
- https://git.kernel.org/stable/c/12391be4724acc9269e1845ccbd881df37de4b56
- https://git.kernel.org/stable/c/15d1cc4b4b585f9a2ce72c52cca004d5d735bdf1
- https://git.kernel.org/stable/c/680ec0549a055eb464dce6ffb4bfb736ef87236e
- https://git.kernel.org/stable/c/fe6921e3b8451a537e01c031b8212366bb386e3e
- https://git.kernel.org/stable/c/00450ed03a17143e2433b461a656ef9cd17c2f1d
- https://git.kernel.org/stable/c/10a089bae827ec30ad9b6cb7048020a62fae0cfa
