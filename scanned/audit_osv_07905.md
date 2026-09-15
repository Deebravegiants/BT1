# [M] Partial password leak over DNS on HTTP redirect

## Summary
Severity: Medium
Advisory: CURL-CVE-2020-8169
Aliases: CVE-2020-8169
Published: 2020-06-24
Source: https://osv.dev/vulnerability/CURL-CVE-2020-8169
Type: osv

## Details
libcurl can be tricked to prepend a part of the password to the hostname
before it resolves it, potentially leaking the partial password over the
network and to the DNS server(s).

libcurl can be given a username and password for HTTP authentication when
requesting an HTTP resource - used for HTTP Authentication such as Basic,
Digest, NTLM and similar. The credentials are set, either together with
`CURLOPT_USERPWD` or separately with `CURLOPT_USERNAME` and
`CURLOPT_PASSWORD`. Important detail: these strings are given to libcurl as
plain C strings and they are not supposed to be URL encoded.

In addition, libcurl also allows the credentials to be set in the URL, using
the standard RFC 3986 format: `http://user:password@host/path`. In this case,
the name and password are URL encoded as that is how they appear in URLs.

If the options are set, they override the credentials set in the URL.

Internally, this is handled by storing the credentials in the "URL object" so
that there is only a single set of credentials stored associated with this
single URL.

When libcurl handles a relative redirect (as opposed to an absolute URL
redirect) for an HTTP transfer, the server is only sending a new path to the
client and that path is applied on to the existing URL. That "applying" of the
relative path on top of an absolute URL is done by libcurl first generating a
full absolute URL out of all the components it has, then it applies the
redirect and finally it deconstructs the URL again into its separate
components.

This security vulnerability originates in the fact that curl did not correctly
URL encode the credential data when set using one of the `curl_easy_setopt`
options described above. This made curl generate a badly formatted full URL
when it would do a redirect and the final re-parsing of the URL would then go
bad and wrongly consider a part of the password field to belong to the host
name.

The wrong hostname would then be used in a name resolve lookup, potentially
leaking the hostname + partial password in clear text over the network (if
plain DNS was used) and in particular to the used DNS server(s).

The password leak is triggered if an at sign (`@`) is used in the password
field, like this: `passw@rd123`. If we also consider a user `dan`, curl would
generate a full URL like:

 `https://dan:passw@rd123@example.com/path`

... while a correct one should have been:

 `https://dan:passw%40rd123@example.com/path`

... when parsing the wrongly generated URL, libcurl would end up with user
name `dan` and password `passw` talking to the host `rd123@example.com`. That
bad hostname would then be passed on to the name resolver function in use
(and for all typical cases return a "cannot resolve hostname" error).

There is no hint in the name resolve as to how large portion of the password
that is actually prepended to the hostname (i.e. an observer does not know how
much data there was on the left side of the `@`), but it can of course be a
significant enough clue for an attacker to figure out the rest.
