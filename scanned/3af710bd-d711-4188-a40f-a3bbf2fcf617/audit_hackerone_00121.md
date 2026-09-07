# [M] Use of uninitialized value of in req_parsebody method of lua_request.c

## Summary
Severity: Medium
Program: Internet Bug Bounty
Weakness: Uncontrolled Resource Consumption
Reporter: chamal
State: resolved
Disclosed: 2022-03-17T15:01:23.600Z
CVE: CVE-2022-22719
Source: https://hackerone.com/reports/1514863

## Details
###Software Versions
Ubuntu - 18.04 64-bit
Apache 2.4.51 - 64 bit

### Cause of Bug
This bug is present in the `req_parsebody` method of lua_request.c file.
Below mentioned lines of code cause this bug.
```cpp
 const char  *data;
 int         i;
 size_t      vlen = 0;
 size_t      len = 0;
 if (lua_read_body(r, &data, (apr_off_t*) &size, max_post_size) != OK) {
     return 2;
 }
 len = strlen(multipart);
 i = 0;
 for
 (
    start = strstr((char *) data, multipart);
 ```

Note that the `const char  *data` pointer is not initialized with a value.
That pointer is passed to the `lua_read_body` method to store data sent by HTTP request.
If the HTTP request does not contain any data, then a value will not be set for `const char  *data` pointer.
So `const char  *data` pointer will remain uninitialized.

Then `const char  *data` pointer is passed as a parameter to "strstr" function.
Segmentation fault will happen in "strstr" function, if it cannot access memory pointed by `const char  *data` pointer.

**I noticed a difference between Apache 64 bit build and 32 bit build.**
    64 bit build - Pointer value of`const char  *data` pointer is 0x1.
                                So a Segmentation fault happens in `strstr` function.
    32 bit build - Pointer value of `const char  *data` pointer has a valid memory address.
                                 So Segmentation fault does NOT happen in `strstr` function.

###Steps
1. Build Apache web server with Lua module

_Trimmed to 38 lines — full report: https://hackerone.com/reports/1514863_
