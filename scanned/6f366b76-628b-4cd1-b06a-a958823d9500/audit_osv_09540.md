# [H] CVE-2017-1000098

## Summary
Severity: High
Advisory: CVE-2017-1000098
Aliases: GO-2021-0172
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/CVE-2017-1000098
Type: osv

## Details
The net/http package's Request.ParseMultipartForm method starts writing to temporary files once the request body size surpasses the given "maxMemory" limit. It was possible for an attacker to generate a multipart request crafted such that the server ran out of file descriptors.

## References
- https://groups.google.com/forum/#%21msg/golang-dev/4NdLzS8sls8/uIz8QlnIBQAJ
- https://golang.org/cl/30410
- https://golang.org/issue/17965
