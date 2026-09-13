# [M] duphandle read out of bounds

## Summary
Severity: Medium
Advisory: CURL-CVE-2014-3707
Aliases: CVE-2014-3707
Published: 2014-11-05
Source: https://osv.dev/vulnerability/CURL-CVE-2014-3707
Type: osv

## Details
libcurl's function
[`curl_easy_duphandle()`](https://curl.se/libcurl/c/curl_easy_duphandle.html)
has a bug that can lead to libcurl eventually sending off sensitive data that
was not intended for sending.

When doing an HTTP POST transfer with libcurl, you can use the
`CURLOPT_COPYPOSTFIELDS` option to specify a memory area holding the data to
send to the remote server. The memory area's size is set with a separate
option, for example `CURLOPT_POSTFIELDSIZE`.

As the name implies, the data in the specified buffer is copied to a privately
held memory buffer that libcurl allocates on the heap. The memory area is
associated with the common CURL handle, often referred to as an "easy handle".

This handle can be duplicated by an application to create an identical copy,
and all the already set options and data is then also similarly cloned and are
be associated with the newly returned handle. This also includes the data to
send in an HTTP POST request.

The internal libcurl function that duplicates options from the old handle to
the new had two problems:

1. It mistakenly treated the post data buffer as if it was a C string which is
   assumed to end with a zero byte. `strdup()` was subsequently used to
   duplicate the post data buffer, and as a post data buffer can both
   legitimately contain a zero byte, or may not contain any zero bytes at all
   (including a tailing one), `strdup()` could create a copy that a) was too
   small b) was too large or c) could crash due to reading an inaccessible
   memory area. The `strdup()` function of course allocates memory off the
   heap.

2. After duplication of the handle data, the pointer used to read from when
   sending the data was not updated. When sending off the post, libcurl would
   still read from the original handle's buffer which at that time could have
   been freed or reused for other purposes.

When libcurl subsequently constructs the HTTP POST request and includes data
for the protocol body it copies data from that pointer using the old size and
the old pointer. This makes a read from the wrong place and can lead to
libcurl inserting data into the request that happens to be stored at that
places in memory at that time.

We are not aware of anyone having been able to actually exploit this for
nefarious purposes, but we cannot exclude that it is possible or even might
already have been exploited.
