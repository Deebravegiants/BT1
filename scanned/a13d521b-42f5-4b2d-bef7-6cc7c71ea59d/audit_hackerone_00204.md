# [H] Out-of-bounds read in iconv.c:_php_iconv_mime_decode() due to integer overflow

## Summary
Severity: High (CVSS 8.2)
Program: Internet Bug Bounty
Weakness: Buffer Over-read
Reporter: neural_x
State: resolved
Disclosed: 2020-10-12T10:51:39.074Z
CVE: CVE-2019-11039
Source: https://hackerone.com/reports/593229

## Details
PHP upstream bug report: https://bugs.php.net/bug.php?id=78069

*Description:*
In _php_iconv_mime_decode() function in iconv.c, there's an out-of-bounds read due to an integer overflow vulnerability. MIME encoded string is being parsed and decoded in for loop with following condition:
```
for (str_left = str_nbytes; str_left > 0; str_left--, p1++) {
```
Inside this for loop, it's possible for str_left to be decreased and p1 to be increased at the same time when scan_stat is equal to 2 (i.e. case 2 branch of the switch) and the given character set is unrecognized and ICONV_MIME_DECODE_CONTINUE_ON_ERROR is specified, so it continues to parse the message. It will then try to skip the encoded word by searching for the other two '?' characters while increasing p1 and decreasing str_left:
```
int qmarks = 2;
while (qmarks > 0 && str_left > 1) {
    if (*(++p1) == '?') {
        --qmarks;
    }
    --str_left;
}
```
If the while condition is stopped, it will proceed to the next condition that checks if the next character is '=' and if it is, p1 is increased again and str_left is decreased: 
```
if (*(p1 + 1) == '=') {
    ++p1;
    --str_left;
}
```
However, if the previous while loop was stopped due to str_left being equal to 1, it is now decreased to 0. The encoded string is copied to 'pretval' variable and if it doesn't error out, it will properly set scan_stat and break:
```
scan_stat = 12;
break;
```
The for loop is being run from start again, but before checking the condition 'str_left > 0', it is first decreased. Since it was already equal to 0 and it is defined as size_t (i.e. unsigned integer), it will overflow to very huge positive number. At this point, the code will continue to read from p1 out of bounds and copy it to 'pretval'.

*PoC:*
```
$ echo "53754c743b2020304a70616100000d0d0d0d0d0d0d0d0d6563743a203d3f69730d0d0d0d0d0d0d0d0d0d0d0d0d0d0d6563743a203d3f6973754c743b2020304a70616100000d0d0d0d0d0d0d0d0d6563743a203d3f6f2d383835392d313f713f3c334633463d33463f3da2" | xxd -r -p - > poc

$ sha256sum poc
c471fb3e1511897d3fda9095e0eb85c934532a207f30ac99f0e7d58c42916e4b  poc

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/593229_
