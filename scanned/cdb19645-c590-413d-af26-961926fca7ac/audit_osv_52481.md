# [H] CVE-2021-47496

## Summary
Severity: High
Advisory: CVE-2021-47496
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-22
Source: https://osv.dev/vulnerability/CVE-2021-47496
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: Fix flipped sign in tls_err_abort() calls

sk->sk_err appears to expect a positive value, a convention that ktls
doesn't always follow and that leads to memory corruption in other code.
For instance,

    [kworker]
    tls_encrypt_done(..., err=<negative error from crypto request>)
      tls_err_abort(.., err)
        sk->sk_err = err;

    [task]
    splice_from_pipe_feed
      ...
        tls_sw_do_sendpage
          if (sk->sk_err) {
            ret = -sk->sk_err;  // ret is positive

    splice_from_pipe_feed (continued)
      ret = actor(...)  // ret is still positive and interpreted as bytes
                        // written, resulting in underflow of buf->len and
                        // sd->len, leading to huge buf->offset and bogus
                        // addresses computed in later calls to actor()

Fix all tls_err_abort() callers to pass a negative error code
consistently and centralize the error-prone sign flip there, throwing in
a warning to catch future misuse and uninlining the function so it
really does only warn once.

## References
- https://git.kernel.org/stable/c/da353fac65fede6b8b4cfe207f0d9408e3121105
- https://git.kernel.org/stable/c/e0cfd5159f314d6b304d030363650b06a2299cbb
- https://git.kernel.org/stable/c/e41473543f75f7dbc5d605007e6f883f1bd13b9a
- https://git.kernel.org/stable/c/f3dec7e7ace38224f82cf83f0049159d067c2e19
