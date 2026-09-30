# [M] Denial of Service attack on windows app using netty

## Summary
Severity: Medium
Advisory: GHSA-xq3w-v528-46rv
CVE: CVE-2024-47535
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-12
Source: https://github.com/advisories/GHSA-xq3w-v528-46rv
Type: github-advisory

## Affected
- Maven: `io.netty:netty-common` — affected >=0 <4.1.115.Final

## Details
### Summary

An unsafe reading of environment file could potentially cause a denial of service in Netty.
When loaded on an Windows application, Netty attemps to load a file that does not exist. If an attacker creates such a large file, the Netty application crash.


### Details

When the library netty is loaded in a java windows application, the library tries to identify the system environnement in which it is executed.

At this stage, Netty tries to load both `/etc/os-release` and `/usr/lib/os-release` even though it is in a Windows environment. 

<img width="364" alt="1" src="https://github.com/user-attachments/assets/9466b181-9394-45a3-b0e3-1dcf105def59">

If netty finds this files, it reads them and loads them into memory.

By default :

- The JVM maximum memory size is set to 1 GB,
- A non-privileged user can create a directory at `C:\` and create files within it.

<img width="340" alt="2" src="https://github.com/user-attachments/assets/43b359a2-5871-4592-ae2b-ffc40ac76831">

<img width="523" alt="3" src="https://github.com/user-attachments/assets/ad5c6eed-451c-4513-92d5-ba0eee7715c1">

the source code identified :
https://github.com/netty/netty/blob/4.1/common/src/main/java/io/netty/util/internal/PlatformDependent.java

Despite the implementation of the function `normalizeOs()` the source code not verify the OS before reading `C:\etc\os-release` and `C:\usr\lib\os-release`.

### PoC

Create a file larger than 1 GB of data in `C:\etc\os-release` or `C:\usr\lib\os-release` on a Windows environnement and start your Netty application.

To observe what the application does with the file, the security analyst used "Process Monitor" from the "Windows SysInternals" suite. (https://learn.microsoft.com/en-us/sysinternals/)

```
cd C:\etc
fsutil file createnew os-release 3000000000
```

<img width="519" alt="4" src="https://github.com/user-attachments/assets/39df22a3-462b-4fd0-af9a-aa30077ec08f">

<img width="517" alt="5" src="https://github.com/user-attachments/assets/129dbd50-fc36-4da5-8eb1-582123fb528f">

The source code used is the Netty website code example : [Echo ‐ the very basic client and server](https://netty.io/4.1/xref/io/netty/example/echo/package-summary.html).

The vulnerability was tested on the 4.1.112.Final version.

The security analyst tried the same technique for `C:\proc\sys\net\core\somaxconn` with a lot of values to impact Netty but the only things that works is the "larger than 1 GB file" technique. https://github.com/netty/netty/blob/c0fdb8e9f8f256990e902fcfffbbe10754d0f3dd/common/src/main/java/io/netty/util/NetUtil.java#L186

### Impact

By loading the "file larger than 1 GB" into the memory, the Netty library exceeds the JVM memory limit and causes a crash in the java Windows application.

This behaviour occurs 100% of the time in both Server mode and Client mode if the large file exists.

Client mode :

<img width="449" alt="6" src="https://github.com/user-attachments/assets/f8fe1ed0-1a42-4490-b9ed-dbc9af7804be">

Server mode :

<img width="464" alt="7" src="https://github.com/user-attachments/assets/b34b42bd-4fbd-4170-b93a-d29ba87b88eb">

somaxconn :

<img width="532" alt="8" src="https://github.com/user-attachments/assets/0656b3bb-32c6-4ae2-bff7-d93babba08a3">

### Severity

- Attack vector : "Local" because the attacker needs to be on the system where the Netty application is running.
- Attack complexity : "Low" because the attacker only need to create a massive file (regardless of its contents).
- Privileges required : "Low" because the attacker requires a user account to exploit the vulnerability.
- User intercation : "None" because the administrator don't need to accidentally click anywhere to trigger the vulnerability. Furthermore, the exploitation works with defaults windows/AD settings.
- Scope : "Unchanged" because only Netty is affected by the vulnerability.
- Confidentiality : "None" because no data is exposed through exploiting the vulnerability.
- Integrity : "None" because the explotation of the vulnerability does not allow editing, deleting or adding data elsewhere.
- Availability : "High" because the exploitation of this vulnerability crashes the entire java application.

## References
- https://github.com/netty/netty/security/advisories/GHSA-xq3w-v528-46rv
- https://nvd.nist.gov/vuln/detail/CVE-2024-47535
- https://github.com/netty/netty/commit/fbf7a704a82e7449b48bd0bbb679f5661c6d61a3
- https://github.com/netty/netty
